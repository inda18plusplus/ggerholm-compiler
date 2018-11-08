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
        self._declare_print_function()

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

    def _declare_print_function(self):
        voidptr_ty = ir.IntType(8).as_pointer()
        printf_ty = ir.FunctionType(ir.IntType(32), [voidptr_ty], var_arg=True)
        printf = ir.Function(self.module, printf_ty, name='printf')
        self.printf = printf

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
