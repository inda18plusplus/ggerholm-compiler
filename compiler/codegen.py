from ctypes import CFUNCTYPE, c_int

from llvmlite import binding, ir


class CodeGen(object):
    def __init__(self):
        self.llvm = binding
        self.llvm.initialize()
        self.llvm.initialize_native_target()
        self.llvm.initialize_native_asmprinter()
        self._config_llvm()
        self._create_execution_engine()

        self._create_types()
        self._declare_global_string('println_number', '%lld\n\0')
        self._declare_global_string('input_number', '%lld\x00')
        self._declare_print_function()
        self._declare_input_function()

    def _create_types(self):
        self.int64 = ir.IntType(64)
        self.int8 = ir.IntType(8)
        self.voidptr = ir.IntType(8).as_pointer()

    def _config_llvm(self):
        self.module = ir.Module(name=__file__)
        self.module.triple = self.llvm.get_default_triple()
        self.builder = ir.IRBuilder()

    def _create_execution_engine(self):
        target = self.llvm.Target.from_default_triple()
        target_machine = target.create_target_machine()
        backing_mod = binding.parse_assembly('')
        engine = binding.create_mcjit_compiler(backing_mod, target_machine)
        self.engine = engine

    def _declare_global_string(self, name, string):
        var_ty = ir.ArrayType(self.int8, len(string))
        var = ir.Constant(var_ty, bytearray(string.encode('utf-8')))
        global_var = ir.GlobalVariable(self.module, var_ty, name)
        global_var.linkage = 'internal'
        global_var.global_constant = True
        global_var.initializer = var

    def _declare_print_function(self):
        printf_ty = ir.FunctionType(self.int64, [self.voidptr], var_arg=True)
        ir.Function(self.module, printf_ty, name='printf')

    def _declare_input_function(self):
        scanf_ty = ir.FunctionType(self.int64, [self.voidptr], var_arg=True)
        ir.Function(self.module, scanf_ty, name='scanf')

    def _compile_ir(self):
        llvm_ir = str(self.module)
        mod = self.llvm.parse_assembly(llvm_ir)
        mod.verify()

        pm_builder = self.llvm.create_pass_manager_builder()
        pm_builder.opt_level = 2
        pm = self.llvm.create_module_pass_manager()
        pm_builder.populate(pm)
        pm.run(mod)

        self.engine.add_module(mod)
        self.engine.finalize_object()
        self.engine.run_static_constructors()

    def run(self, recompile=True):
        if recompile:
            self.create_ir()
        main_function = CFUNCTYPE(c_int)(self.engine.get_function_address('main'))
        return main_function()

    def create_ir(self):
        self._compile_ir()

    def save_ir(self, filename):
        with open(filename, 'w') as f:
            f.write(str(self.module))
