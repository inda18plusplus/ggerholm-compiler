from rply import LexerGenerator


class Lexer(object):
    def __init__(self):
        self.lexer = LexerGenerator()

    def _add_tokens(self):
        self.lexer.add('PRINT', r'print')
        self.lexer.add('OPEN_PAREN', r'\(')
        self.lexer.add('CLOSE_PAREN', r'\)')
        self.lexer.add('SEMICOLON', r';')
        self.lexer.add('SUM', r'\+')
        self.lexer.add('SUB', r'\-')
        self.lexer.add('NUMBER', r'\d+')
        self.lexer.add('MUL', r'\*')
        self.lexer.add('DIV', r'/')
        self.lexer.add('NOT', r'!')
        self.lexer.add('COMPLEMENT', r'~')
        self.lexer.add('PRIMITIVE_DATA_TYPE', r'int')
        self.lexer.add('OPEN_CURLY', r'{')
        self.lexer.add('CLOSE_CURLY', r'}')
        self.lexer.add('RETURN', r'return')
        self.lexer.add('IF', r'if')
        self.lexer.add('ELSE', r'else')
        self.lexer.add('EQUALS', r'==')
        self.lexer.add('NOT_EQUALS', r'!=')
        self.lexer.add('EQUAL_SIGN', r'=')
        self.lexer.add('FOR', r'for')
        self.lexer.add('LESS', r'<')
        self.lexer.add('GREATER', r'>')
        self.lexer.add('LESS_EQ', r'<=')
        self.lexer.add('GREATER_EQ', r'>=')
        self.lexer.add('EQUALS', r'==')
        self.lexer.add('COMMA', r',')
        self.lexer.add('IDENTIFIER', r'[a-zA-Z]\w*')
        self.lexer.ignore(r'\s+')

    def get_lexer(self):
        self._add_tokens()
        return self.lexer.build()
