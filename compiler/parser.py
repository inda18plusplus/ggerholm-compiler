from rply import ParserGenerator

from compiler.ast import Number, Negate, BitComplement, Not, Print, Function, FunctionCall, \
    FunctionPrototype, Program, IfStatement, ForLoop, BinaryOp


class ParserState(object):
    pass


class Parser(object):
    def __init__(self, module, builder, printf):
        self.pg = ParserGenerator([
            'NUMBER', 'PRINT', 'OPEN_PAREN', 'CLOSE_PAREN', 'SEMICOLON', 'SUM', 'SUB', 'MUL', 'DIV', 'NOT',
            'COMPLEMENT', 'OPEN_CURLY', 'CLOSE_CURLY', 'PRIMITIVE_DATA_TYPE', 'RETURN', 'IDENTIFIER',
            'IF', 'ELSE', 'FOR', 'GREATER', 'LESS', 'GREATER_EQ', 'LESS_EQ', 'EQUALS', 'NOT_EQUALS'
        ], precedence=[
            ('left', ['SUM', 'SUB']),
            ('left', ['MUL', 'DIV']),
            ('left', ['NOT', 'COMPLEMENT']),
            ('left', ['GREATER', 'GREATER_EQ', 'LESS', 'LESS_EQ']),
            ('left', ['EQUALS', 'NOT_EQUALS'])
        ])

        self.module = module
        self.builder = builder
        self.printf = printf

    def parse(self):

        @self.pg.production('program : function')
        @self.pg.production('program : program function')
        def program(state, p):
            functions = []
            if len(p) > 1:
                functions.extend(p[0].functions)
                functions.append(p[1])
            else:
                functions.append(p[0])
            return Program(self.builder, self.module, functions)

        # TODO: Make pretty

        @self.pg.production("""function :
                               PRIMITIVE_DATA_TYPE IDENTIFIER OPEN_PAREN CLOSE_PAREN OPEN_CURLY
                               statement
                               RETURN statement
                               CLOSE_CURLY""")
        def func(state, p):
            prototype = FunctionPrototype(self.builder, self.module, p[1])
            body = p[5]
            return_val = p[7]
            return Function(self.builder, self.module, prototype, body, return_val)

        @self.pg.production('function_call : IDENTIFIER OPEN_PAREN CLOSE_PAREN')
        def func_call(state, p):
            return FunctionCall(self.builder, self.module, p[0])

        @self.pg.production('print : PRINT OPEN_PAREN expression CLOSE_PAREN')
        def print_stmt(state, p):
            return Print(self.builder, self.module, self.printf, p[2])

        @self.pg.production("""if_stmt :
                               IF OPEN_PAREN bool_exp CLOSE_PAREN OPEN_CURLY
                               statement CLOSE_CURLY ELSE OPEN_CURLY
                               statement CLOSE_CURLY""")
        def if_stmt(state, p):
            condition = p[2]
            then_exp = p[5]
            else_exp = p[9]
            return IfStatement(self.builder, self.module, condition, then_exp, else_exp)

        @self.pg.production("""for_loop :
                               FOR OPEN_PAREN expression SEMICOLON
                               expression SEMICOLON expression CLOSE_PAREN OPEN_CURLY
                               statement CLOSE_CURLY""")
        def for_loop(state, p):
            return ForLoop(self.builder, self.module, state, p[2], p[4], p[6], p[9])

        @self.pg.production('statement : expression SEMICOLON')
        @self.pg.production('statement : function_call SEMICOLON')
        @self.pg.production('statement : print SEMICOLON')
        @self.pg.production('statement : if_stmt')
        @self.pg.production('statement : for_loop')
        def statement(state, p):
            return p[0]

        @self.pg.production('expression : OPEN_PAREN expression CLOSE_PAREN')
        def expression_parentheses(state, p):
            return p[1]

        @self.pg.production('expression : expression SUM expression')
        @self.pg.production('expression : expression SUB expression')
        @self.pg.production('expression : expression MUL expression')
        @self.pg.production('expression : expression DIV expression')
        @self.pg.production('bool_exp : expression LESS expression')
        @self.pg.production('bool_exp : expression GREATER expression')
        @self.pg.production('bool_exp : expression LESS_EQ expression')
        @self.pg.production('bool_exp : expression GREATER_EQ expression')
        @self.pg.production('bool_exp : expression EQUALS expression')
        @self.pg.production('bool_exp : expression NOT_EQUALS expression')
        def binary_op(state, p):
            left = p[0]
            right = p[2]
            operator = p[1].value
            return BinaryOp(self.builder, self.module, operator, left, right)

        @self.pg.production('expression : SUB expression')
        @self.pg.production('expression : COMPLEMENT expression')
        @self.pg.production('expression : NOT expression')
        def unary_op(state, p):
            operator = p[0]
            value = p[1]
            if operator.gettokentype() == 'SUB':
                return Negate(self.builder, self.module, value)
            elif operator.gettokentype() == 'COMPLEMENT':
                return BitComplement(self.builder, self.module, value)
            elif operator.gettokentype() == 'NOT':
                return Not(self.builder, self.module, value)

        @self.pg.production('expression : NUMBER')
        def number(state, p):
            return Number(self.builder, self.module, p[0].value)

        @self.pg.error
        def error_handle(state, token):
            raise ValueError(token)

    def get_parser(self):
        return self.pg.build()
