from rply import ParserGenerator

from compiler.ast import Sum, Sub, Number, Negate, BitComplement, Not, Div, Mul, Print


class Parser(object):
    def __init__(self, module, builder, printf):
        self.pg = ParserGenerator([
            'NUMBER', 'PRINT', 'OPEN_PAREN', 'CLOSE_PAREN', 'SEMICOLON', 'SUM', 'SUB', 'MUL', 'DIV', 'NOT',
            'COMPLEMENT'
        ], precedence=[
            ('left', ['SUM', 'SUB']),
            ('left', ['MUL', 'DIV']),
            ('left', ['NOT', 'COMPLEMENT'])
        ])

        self.module = module
        self.builder = builder
        self.printf = printf

    def parse(self):
        @self.pg.production('program : PRINT OPEN_PAREN expression CLOSE_PAREN SEMICOLON')
        def program(p):
            return Print(self.builder, self.module, self.printf, p[2])

        @self.pg.production('expression : OPEN_PAREN expression CLOSE_PAREN')
        def expression_parentheses(p):
            return p[1]

        @self.pg.production('expression : expression SUM expression')
        @self.pg.production('expression : expression SUB expression')
        @self.pg.production('expression : expression MUL expression')
        @self.pg.production('expression : expression DIV expression')
        def binary_op(p):
            left = p[0]
            right = p[2]
            operator = p[1]
            if operator.gettokentype() == 'SUM':
                return Sum(self.builder, self.module, left, right)
            elif operator.gettokentype() == 'SUB':
                return Sub(self.builder, self.module, left, right)
            elif operator.gettokentype() == 'MUL':
                return Mul(self.builder, self.module, left, right)
            elif operator.gettokentype() == 'DIV':
                return Div(self.builder, self.module, left, right)

        @self.pg.production('expression : SUB expression')
        @self.pg.production('expression : COMPLEMENT expression')
        @self.pg.production('expression : NOT expression')
        def unary_op(p):
            operator = p[0]
            value = p[1]
            if operator.gettokentype() == 'SUB':
                return Negate(self.builder, self.module, value)
            elif operator.gettokentype() == 'COMPLEMENT':
                return BitComplement(self.builder, self.module, value)
            elif operator.gettokentype() == 'NOT':
                return Not(self.builder, self.module, value)

        @self.pg.production('expression : NUMBER')
        def number(p):
            return Number(self.builder, self.module, p[0].value)

        @self.pg.error
        def error_handle(token):
            raise ValueError(token)

    def get_parser(self):
        return self.pg.build()
