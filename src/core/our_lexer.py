from ply import *

keywords = (
    'IF', 'THEN', 'RETURN',
    'TRUE', 'FALSE', 'AND', 'OR', 'NOT', 'GAUSS', 'EPS',
    'RANDOM', 'NUMERIC', 'ELSE', 'OUTPUT', 'INPUT', 'INPUTSIZE'
)

tokens = keywords + (
    'EQUALS', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'POWER',
    'LPAREN', 'RPAREN', 'LT', 'LE', 'GT', 'GE', 'NE',
    'COMMA', 'SEMI', 'INTEGER', 'FLOAT', 'STRING',
    'ID', 'NEWLINE', 'LCURLY', 'RCURLY', 'LBRACKET', 'RBRACKET'
)

t_ignore = ' \t'


def t_ID(t):
    r'[A-Z][A-Z0-9]*'
    if t.value in keywords:
        t.type = t.value
    return t


t_EQUALS = r'='
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_POWER = r'\^'
t_DIVIDE = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LT = r'<'
t_LE = r'<='
t_GT = r'>'
t_GE = r'>='
t_NE = r'<>'
t_COMMA = r'\,'
t_SEMI = r';'
# t_TRUE = r'true'
# t_FALSE = r'false'
# t_AND
t_RANDOM = r'RANDOM'
t_GAUSS = r'gauss'
t_EPS = r'eps'
t_LCURLY = r'\{'
t_RCURLY = r'\}'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_INTEGER = r'\d+'
t_FLOAT = r'((\d*\.\d+)(E[\+-]?\d+)?|([1-9]\d*E[\+-]?\d+))'
t_STRING = r'\".*?\"'


def t_NEWLINE(t):
    r'\n'
    t.lexer.lineno += 1
    return t


def t_error(t):
    # print(t)
    print("Illegal character %s" % t.value[0])
    t.lexer.skip(1)


lex.lex(debug=0)
