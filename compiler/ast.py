from llvmlite import ir

int_type = ir.IntType(8)


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
            self.builder.icmp_unsigned('==', self.value.eval(), ir.Constant(int_type, 0)),
            ir.Constant(int_type, 1), ir.Constant(int_type, 0))


class BitComplement(UnaryOp):
    def eval(self):
        return self.builder.not_(self.value.eval())


class Negate(UnaryOp):
    def eval(self):
        return self.builder.neg(self.value.eval())


class BinaryOp(object):
    def __init__(self, builder, module, left, right):
        self.builder = builder
        self.module = module
        self.left = left
        self.right = right


class Sum(BinaryOp):
    def eval(self):
        return self.builder.add(self.left.eval(), self.right.eval())


class Sub(BinaryOp):
    def eval(self):
        return self.builder.sub(self.left.eval(), self.right.eval())


class Mul(BinaryOp):
    def eval(self):
        return self.builder.mul(self.left.eval(), self.right.eval())


class Div(BinaryOp):
    def eval(self):
        return self.builder.udiv(self.left.eval(), self.right.eval())


class Print(object):
    def __init__(self, builder, module, printf, value):
        self.builder = builder
        self.module = module
        self.printf = printf
        self.value = value

    def eval(self):
        value = self.value.eval()

        voidptr_ty = int_type.as_pointer()
        fmt = '%i \n\0'
        c_fmt = ir.Constant(ir.ArrayType(int_type, len(fmt)), bytearray(fmt.encode('utf-8')))

        global_fmt = ir.GlobalVariable(self.module, c_fmt.type, name='fstr')
        global_fmt.linkage = 'internal'
        global_fmt.global_constant = True
        global_fmt.initializer = c_fmt
        fmt_arg = self.builder.bitcast(global_fmt, voidptr_ty)

        self.builder.call(self.printf, [fmt_arg, value])
