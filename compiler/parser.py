from rply import ParserGenerator

from compiler.ast import Number, Print, Function, FunctionCall, \
    FunctionPrototype, Program, IfStatement, ForLoop, BinaryOp, Variable, UnaryOp


class ParserState(object):
    func_symbols = {}


class Parser(object):
    def __init__(self, cg):
        self.pg = ParserGenerator([
            'NUMBER', 'PRINT', 'OPEN_PAREN', 'CLOSE_PAREN', 'SEMICOLON', 'SUM', 'SUB', 'MUL', 'DIV', 'NOT',
            'COMPLEMENT', 'OPEN_CURLY', 'CLOSE_CURLY', 'PRIMITIVE_DATA_TYPE', 'RETURN', 'IDENTIFIER',
            'IF', 'ELSE', 'FOR', 'GREATER', 'LESS', 'GREATER_EQ', 'LESS_EQ', 'EQUALS', 'NOT_EQUALS',
            'COMMA', 'EQUAL_SIGN'
        ], precedence=[
            ('left', ['EQUALS', 'NOT_EQUALS', 'GREATER', 'GREATER_EQ', 'LESS', 'LESS_EQ']),
            ('right', ['EQUAL_SIGN']),
            ('left', ['SUM', 'SUB']),
            ('left', ['MUL', 'DIV']),
            ('right', ['NOT', 'COMPLEMENT'])
        ])

        self.cg = cg

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
            return Program(self.cg, state, functions)

        @self.pg.production('body : statement')
        @self.pg.production('body : body statement')
        def body(state, p):
            if len(p) == 1:
                return [p[0]]
            return p[0] + [p[1]]

        @self.pg.production("""function :
                               func_proto OPEN_CURLY
                               body
                               RETURN statement
                               CLOSE_CURLY""")
        def func(state, p):
            return Function(self.cg, state, p[0], p[2], p[4])

        @self.pg.production('func_proto : PRIMITIVE_DATA_TYPE IDENTIFIER OPEN_PAREN CLOSE_PAREN')
        @self.pg.production('func_proto : PRIMITIVE_DATA_TYPE IDENTIFIER OPEN_PAREN arg_names CLOSE_PAREN')
        def func_prototype(state, p):
            if len(p) > 4:
                return FunctionPrototype(self.cg, state, p[1].value, p[3])
            return FunctionPrototype(self.cg, state, p[1].value, [])

        @self.pg.production('arg_names : IDENTIFIER')
        @self.pg.production('arg_names : arg_names COMMA IDENTIFIER')
        def arg_names(state, p):
            if len(p) == 1:
                return [p[0].value]
            return p[0] + [p[2].value]

        @self.pg.production('arg_values : expression')
        @self.pg.production('arg_values : arg_values COMMA expression')
        def arg_values(state, p):
            if len(p) == 1:
                return [p[0]]
            return p[0] + [p[2]]

        @self.pg.production('function_call : IDENTIFIER OPEN_PAREN CLOSE_PAREN')
        @self.pg.production('function_call : IDENTIFIER OPEN_PAREN arg_values CLOSE_PAREN')
        def func_call(state, p):
            if len(p) > 3:
                return FunctionCall(self.cg, state, p[0].value, p[2])
            return FunctionCall(self.cg, state, p[0].value, [])

        @self.pg.production('print : PRINT OPEN_PAREN expression CLOSE_PAREN')
        def print_stmt(state, p):
            return Print(self.cg, state, p[2])

        @self.pg.production("""if_stmt :
                               IF OPEN_PAREN bool_exp CLOSE_PAREN OPEN_CURLY
                               body CLOSE_CURLY ELSE OPEN_CURLY
                               body CLOSE_CURLY""")
        def if_stmt(state, p):
            condition = p[2]
            then_body = p[5]
            else_body = p[9]
            return IfStatement(self.cg, state, condition, then_body, else_body)

        @self.pg.production("""for_loop :
                               FOR OPEN_PAREN IDENTIFIER EQUAL_SIGN expression SEMICOLON
                               bool_exp SEMICOLON expression CLOSE_PAREN OPEN_CURLY
                               body CLOSE_CURLY""")
        def for_loop(state, p):
            return ForLoop(self.cg, state, p[2].value, p[4], p[6], p[8], p[11])

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
        @self.pg.production('bool_exp : expression LESS_EQ expression')
        @self.pg.production('bool_exp : expression GREATER_EQ expression')
        @self.pg.production('bool_exp : expression LESS expression')
        @self.pg.production('bool_exp : expression GREATER expression')
        @self.pg.production('bool_exp : expression EQUALS expression')
        @self.pg.production('bool_exp : expression NOT_EQUALS expression')
        def binary_op(state, p):
            left = p[0]
            right = p[2]
            operator = p[1].gettokentype()
            return BinaryOp(self.cg, state, operator, left, right)

        @self.pg.production('expression : IDENTIFIER EQUAL_SIGN expression')
        def var_assignment(state, p):
            var = variable(state, p)
            return BinaryOp(self.cg, state, 'EQUAL_SIGN', var, p[2])

        @self.pg.production('expression : SUB expression')
        @self.pg.production('expression : COMPLEMENT expression')
        @self.pg.production('expression : NOT expression')
        def unary_op(state, p):
            operator = p[0].gettokentype()
            value = p[1]
            return UnaryOp(self.cg, state, operator, value)

        @self.pg.production('expression : NUMBER')
        def number(state, p):
            return Number(self.cg, state, p[0].value)

        @self.pg.production('expression : IDENTIFIER')
        def variable(state, p):
            return Variable(self.cg, state, p[0].value)

        @self.pg.error
        def error_handle(state, token):
            raise ValueError(token)

    def get_parser(self):
        return self.pg.build()
