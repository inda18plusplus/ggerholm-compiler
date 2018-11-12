from llvmlite import ir

from compiler.errors import CodeGenError

data_type = ir.IntType(32)


class Program(object):
    def __init__(self, builder, module, state, functions):
        self.builder = builder
        self.module = module
        self.state = state
        self.functions = functions

    def generate(self):
        main = None
        for func in self.functions:
            if func.prototype.name == 'main':
                main = func
            else:
                func.generate()
        if not main:
            raise CodeGenError('No main function')
        return main.generate()


class FunctionPrototype(object):
    def __init__(self, builder, module, state, name, arg_names):
        self.builder = builder
        self.module = module
        self.state = state
        self.name = name
        self.arg_names = arg_names

    def generate(self):
        func_name = self.name
        func_ty = ir.FunctionType(data_type, [data_type] * len(self.arg_names), False)
        if func_name in self.module.globals:
            func = self.module[func_name]
            if not isinstance(func, ir.Function):
                raise CodeGenError('Function / Global name collision', func_name)
            if not func.is_declaration():
                raise CodeGenError('Redefinition of {0}', func_name)
            if len(func.function_type.args) != 0:
                raise CodeGenError('Redefinition with different number of arguments')
        else:
            func = ir.Function(self.module, func_ty, func_name)

        return func


class Function(object):
    def __init__(self, builder, module, state, prototype, body, return_value):
        self.builder = builder
        self.module = module
        self.state = state
        self.prototype = prototype
        self.body = body
        self.return_value = return_value

    def generate(self):
        self.state.func_symbols = {}
        func = self.prototype.generate()
        block = func.append_basic_block('entry')
        self.builder.position_at_end(block)

        for i, arg in enumerate(func.args):
            arg.name = self.prototype.arg_names[i]
            address = self.builder.alloca(data_type, name=arg.name)
            self.builder.store(arg, address)
            self.state.func_symbols[arg.name] = address

        for stmt in self.body:
            stmt.generate()

        result = self.return_value.generate()
        self.builder.ret(result)
        return func


class FunctionCall(object):
    def __init__(self, builder, module, state, name, args):
        self.builder = builder
        self.module = module
        self.state = state
        self.name = name
        self.args = args

    def generate(self):
        callee_func = self.module.globals.get(self.name, None)
        if not callee_func or not isinstance(callee_func, ir.Function):
            raise CodeGenError('Call to unknown function', self.name)
        if len(callee_func.args) != len(self.args):
            raise CodeGenError('Incorrect number of arguments', self.name)
        call_args = [arg.generate() for arg in self.args]
        return self.builder.call(callee_func, call_args)


class IfStatement(object):
    def __init__(self, builder, module, state, condition, then_body, else_body):
        self.builder = builder
        self.module = module
        self.state = state
        self.condition = condition
        self.then_body = then_body
        self.else_body = else_body

    def generate(self):
        cond_val = self.condition.generate()

        then_block = self.builder.function.append_basic_block('then')
        else_block = ir.Block(self.builder.function, 'else')
        merge_block = ir.Block(self.builder.function, 'if_block')
        self.builder.cbranch(cond_val, then_block, else_block)
        self.builder.position_at_start(then_block)
        then_val = self.then_body[0].generate()
        for stmt in self.then_body[1:]:
            stmt.generate()
        self.builder.branch(merge_block)

        then_block = self.builder.block

        self.builder.function.basic_blocks.append(else_block)
        self.builder.position_at_start(else_block)
        else_val = self.else_body[0].generate()
        for stmt in self.else_body[1:]:
            stmt.generate()
        self.builder.branch(merge_block)

        self.builder.function.basic_blocks.append(merge_block)
        self.builder.position_at_start(merge_block)
        phi = self.builder.phi(data_type, 'if_phi')
        phi.add_incoming(then_val, then_block)
        phi.add_incoming(else_val, else_block)
        return phi


class ForLoop(object):
    def __init__(self, builder, module, state, var_name, start, end_cond, step, body):
        self.builder = builder
        self.module = module
        self.state = state
        self.var_name = var_name
        self.start = start
        self.end_cond = end_cond
        self.step = step
        self.body = body

    # TODO: Handle < > and prevent loop body when the initial condition is false.
    def generate(self):
        saved_block = self.builder.block
        self.builder.goto_entry_block()
        var_address = self.builder.alloca(data_type, name=self.var_name)
        self.builder.position_at_end(saved_block)

        start_val = self.start.generate()
        self.builder.store(start_val, var_address)
        loop_block = self.builder.function.append_basic_block('loop')

        self.builder.branch(loop_block)
        self.builder.position_at_start(loop_block)

        # Save the variable value in case the name 'i' shadows it
        old_var_address = self.state.func_symbols.get(self.var_name)
        self.state.func_symbols[self.var_name] = var_address

        # Add the loop body
        for stmt in self.body:
            stmt.generate()

        # Decide how much to step
        if self.step is None:
            step_val = ir.Constant(data_type, 1)
        else:
            step_val = self.step.generate()
        cur_var = self.builder.load(var_address, self.var_name)
        next_value = self.builder.add(cur_var, step_val, 'next_value')
        self.builder.store(next_value, var_address)

        # Decide whether or not to break the loop
        end_val = self.end_cond.generate()
        cmp = self.builder.icmp_signed('!=', end_val, ir.Constant(data_type, 0), 'loop_cond')

        after_block = self.builder.function.append_basic_block('after_loop')
        self.builder.cbranch(cmp, loop_block, after_block)
        self.builder.position_at_start(after_block)

        # Restore the old variable value in case the name 'i' shadowed it
        if old_var_address is not None:
            self.state.func_symbols[self.var_name] = old_var_address
        else:
            del self.state.func_symbols[self.var_name]

        return ir.Constant(data_type, 0)


class Variable(object):
    def __init__(self, builder, module, state, name):
        self.builder = builder
        self.module = module
        self.state = state
        self.name = name

    def generate(self):
        var_address = self.state.func_symbols[self.name]
        return self.builder.load(var_address, self.name)


class Number(object):
    def __init__(self, builder, module, state, value):
        self.builder = builder
        self.module = module
        self.state = state
        self.value = value

    def generate(self):
        return ir.Constant(data_type, int(self.value))


class UnaryOp(object):
    def __init__(self, builder, module, state, value):
        self.builder = builder
        self.module = module
        self.state = state
        self.value = value


class Not(UnaryOp):
    def generate(self):
        return self.builder.select(
            self.builder.icmp_signed('==', self.value.generate(), ir.Constant(data_type, 0)),
            ir.Constant(data_type, 1), ir.Constant(data_type, 0))


class BitComplement(UnaryOp):
    def generate(self):
        return self.builder.not_(self.value.generate())


class Negate(UnaryOp):
    def generate(self):
        return self.builder.neg(self.value.generate())


class BinaryOp(object):
    def __init__(self, builder, module, state, operator, left, right):
        self.builder = builder
        self.module = module
        self.state = state
        self.operator = operator
        self.left = left
        self.right = right

    def generate(self):
        op = self.operator
        if op == '=':
            if not isinstance(self.left, Variable):
                raise CodeGenError('Invalid assignment')
            var_address = self.state.func_symbols[self.left.name]
            value = self.right.generate()
            self.builder.store(value, var_address)
            return value
        elif op == '+':
            return self.builder.add(self.left.generate(), self.right.generate())
        elif op == '-':
            return self.builder.sub(self.left.generate(), self.right.generate())
        elif op == '*':
            return self.builder.mul(self.left.generate(), self.right.generate())
        elif op == '/':
            return self.builder.sdiv(self.left.generate(), self.right.generate())
        elif op == '<' or op == '<=' or op == '>' or op == '>=' or op == '==' or op == '!=':
            return self.builder.icmp_signed(op, self.left.generate(), self.right.generate())


class Print(object):
    def __init__(self, builder, module, state, printf, value):
        self.builder = builder
        self.module = module
        self.state = state
        self.printf = printf
        self.value = value

    def generate(self):
        value = self.value.generate()

        voidptr_ty = ir.IntType(8).as_pointer()
        fmt = '%i \n\0'
        c_fmt = ir.Constant(ir.ArrayType(ir.IntType(8), len(fmt)), bytearray(fmt.encode('utf-8')))

        global_fmt = self.module.globals.get('f_str')
        if not global_fmt:
            global_fmt = ir.GlobalVariable(self.module, c_fmt.type, name='f_str')
            global_fmt.linkage = 'internal'
            global_fmt.global_constant = True
            global_fmt.initializer = c_fmt
        fmt_arg = self.builder.bitcast(global_fmt, voidptr_ty)

        return self.builder.call(self.printf, [fmt_arg, value])
