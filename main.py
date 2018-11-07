from compiler.codegen import CodeGen
from compiler.lexer import Lexer
from compiler.parser import Parser, ParserState


def main():
    with open('example.unnamedlang', 'r') as f:
        text_input = f.read()

    lexer = Lexer().get_lexer()
    tokens = lexer.lex(text_input)

    cg = CodeGen()
    module = cg.module
    builder = cg.builder
    printf = cg.printf

    pg = Parser(module, builder, printf)
    pg.parse()
    parser = pg.get_parser()
    parser.parse(tokens, state=ParserState()).eval()

    cg.create_ir()
    cg.save_ir('output/output.ll')


if __name__ == '__main__':
    main()
