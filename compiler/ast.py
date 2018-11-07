from llvmlite import ir

from compiler.errors import CodeGenError

int_type = ir.IntType(32)


class Program(object):
    def __init__(self, builder, module, functions):
        self.builder = builder
        self.module = module
        self.functions = functions

    def eval(self):
        main = None
        for func in self.functions:
            if func.prototype.name.value == 'main':
                main = func
            else:
                func.eval()
        if not main:
            raise CodeGenError('No main function')
        return main.eval()


class FunctionPrototype(object):
    def __init__(self, builder, module, name):
        self.builder = builder
        self.module = module
        self.name = name

    def eval(self):
        func_name = self.name.value
        if func_name in self.module.globals:
            existing_func = self.module[func_name]
            if not isinstance(existing_func, ir.Function):
                raise CodeGenError('Function / Global name collision', func_name)
            if not existing_func.is_declaration():
                raise CodeGenError('Redefinition of {0}', func_name)
            if len(existing_func.function_type.args) != 0:
                raise CodeGenError('Redefinition with different number of arguments')
        else:
            func_ty = ir.FunctionType(int_type, [], False)
            return ir.Function(self.module, func_ty, func_name)


class Function(object):
    def __init__(self, builder, module, prototype, body, return_value):
        self.builder = builder
        self.module = module
        self.prototype = prototype
        self.body = body
        self.return_value = return_value

    def eval(self):
        func = self.prototype.eval()
        block = func.append_basic_block('entry')
        self.builder.position_at_end(block)
        self.body.eval()
        result = self.return_value.eval()
        self.builder.ret(result)
        return func


class FunctionCall(object):
    def __init__(self, builder, module, name):
        self.builder = builder
        self.module = module
        self.name = name

    def eval(self):
        callee_func = self.module.globals.get(self.name.value, None)
        if not callee_func or not isinstance(callee_func, ir.Function):
            raise CodeGenError('Call to unknown function', self.name.value)
        return self.builder.call(callee_func, [])


class IfStatement(object):
    def __init__(self, builder, module, condition, then_exp, else_exp):
        self.builder = builder
        self.module = module
        self.condition = condition
        self.then_exp = then_exp
        self.else_exp = else_exp

    def eval(self):
        cond_val = self.condition.eval()

        then_block = self.builder.function.append_basic_block('then')
        else_block = ir.Block(self.builder.function, 'else')
        merge_block = ir.Block(self.builder.function, 'if_mrg')
        self.builder.cbranch(cond_val, then_block, else_block)
        self.builder.position_at_start(then_block)
        then_val = self.then_exp.eval()
        self.builder.branch(merge_block)

        then_block = self.builder.block

        self.builder.function.basic_blocks.append(else_block)
        self.builder.position_at_start(else_block)
        else_val = self.else_exp.eval()
        self.builder.branch(merge_block)

        self.builder.function.basic_blocks.append(merge_block)
        self.builder.position_at_start(merge_block)
        phi = self.builder.phi(int_type, 'if_temp')
        phi.add_incoming(then_val, then_block)
        phi.add_incoming(else_val, else_block)
        return phi


class ForLoop(object):
    def __init__(self, builder, module, state, start, end, step, body):
        self.builder = builder
        self.module = module
        self.state = state
        self.start = start
        self.end = end
        self.step = step
        self.body = body

    def eval(self):
        start_val = self.start.eval()
        entry_block = self.builder.block
        loop_block = self.builder.function.append_basic_block('loop')

        self.builder.branch(loop_block)
        self.builder.position_at_start(loop_block)

        phi = self.builder.phi(int_type, 'count')
        phi.add_incoming(start_val, entry_block)

        self.body.eval()

        if self.step is None:
            step_val = ir.Constant(int_type, 1)
        else:
            step_val = self.step.eval()
        next_var = self.builder.add(phi, step_val, 'next_var')
        end_val = self.end.eval()
        cmp = self.builder.icmp_signed('!=', next_var, end_val, 'loop_cond')
        # TODO: Handle < > and prevent loop body when the initial condition is false.

        loop_end_block = self.builder.block
        after_block = self.builder.function.append_basic_block('after_loop')

        self.builder.cbranch(cmp, loop_block, after_block)

        self.builder.position_at_start(after_block)

        phi.add_incoming(next_var, loop_end_block)

        return ir.Constant(int_type, 0)


class Number(object):
    def __init__(self, builder, module, value):
        self.builder = builder
        self.module = module
        self.value = value

    def eval(self):
        return ir.Constant(int_type, int(self.value))


class UnaryOp(object):
    def __init__(self, builder, module, value):
        self.builder = builder
        self.module = module
        self.value = value


class Not(UnaryOp):
    def eval(self):
        return self.builder.select(
            self.builder.icmp_signed('==', self.value.eval(), ir.Constant(int_type, 0)),
            ir.Constant(int_type, 1), ir.Constant(int_type, 0))


class BitComplement(UnaryOp):
    def eval(self):
        return self.builder.not_(self.value.eval())


class Negate(UnaryOp):
    def eval(self):
        return self.builder.neg(self.value.eval())


class BinaryOp(object):
    def __init__(self, builder, module, operator, left, right):
        self.builder = builder
        self.module = module
        self.operator = operator
        self.left = left
        self.right = right

    def eval(self):
        op = self.operator
        if op == '+':
            return self.builder.add(self.left.eval(), self.right.eval())
        elif op == '-':
            return self.builder.sub(self.left.eval(), self.right.eval())
        elif op == '*':
            return self.builder.mul(self.left.eval(), self.right.eval())
        elif op == '/':
            return self.builder.sdiv(self.left.eval(), self.right.eval())
        elif op == '<' or op == '<=' or op == '>' or op == '>=' or op == '==' or op == '!=':
            return self.builder.icmp_signed(op, self.left.eval(), self.right.eval())


class Print(object):
    def __init__(self, builder, module, printf, value):
        self.builder = builder
        self.module = module
        self.printf = printf
        self.value = value

    def eval(self):
        value = self.value.eval()

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

        self.builder.call(self.printf, [fmt_arg, value])
