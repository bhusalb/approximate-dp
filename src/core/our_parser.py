from ply import *

from . import our_lexer

tokens = our_lexer.tokens

precedence = (
    # ('left', 'PLUS', 'MINUS'),
    # ('left', 'TIMES', 'DIVIDE'),
    # ('left', 'POWER'),
    # ('right', 'UMINUS')
)


# A BASIC program is a series of statements.  We represent the program as a
# dictionary of tuples indexed by line number.


def p_program(p):
    '''program : program statement
               | statement'''

    if len(p) >= 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]


# This catch-all rule is used for any catastrophic errors.  In this case,
# we simply return nothing


def p_statement(p):
    '''statement : random_var_assignment SEMI
                  | numeric_var_assignment SEMI
                  | ifblock
                  | ifelseblock
                  | setinputsize SEMI
                  | inputassignment SEMI
                  | outputassignment SEMI
                  | setoutput SEMI
    '''
    # print(p[1])
    p[0] = p[1]


def p_statement_newline(p):
    '''statement : statement NEWLINE'''
    p[0] = p[1]


def p_statement_newline_2(p):
    '''statement : NEWLINE statement'''
    p[0] = p[2]


def p_input(p):
    '''inputassignment : INPUT EQUALS LBRACKET numlist RBRACKET COMMA LBRACKET numlist RBRACKET'''
    p[0] = 'INPUT', p[4], p[8]


def p_output(p):
    '''outputassignment : OUTPUT EQUALS LBRACKET numlist RBRACKET'''
    p[0] = 'OUTPUT', p[4]


def p_statement_random_variable(p):
    '''random_var_assignment : RANDOM variable EQUALS gaussfunc'''

    p[0] = ('assignment', 'GAUSS', p[2], p[4])


def p_statement_numeric_variable(p):
    """numeric_var_assignment : NUMERIC variable EQUALS number"""
    p[0] = ('assignment', 'NUMERIC', p[2], p[4])


def p_gauss(p):
    """gaussfunc : GAUSS LPAREN EPS DIVIDE number COMMA variable RPAREN
                | GAUSS LPAREN EPS DIVIDE number COMMA number RPAREN
                | GAUSS LPAREN EPS DIVIDE number COMMA inputindex RPAREN
    """
    p[0] = p[5], p[7]


def p_get_input_index(p):
    '''inputindex : INPUT LBRACKET INTEGER RBRACKET'''
    p[0] = 'INDEX', int(p[3])


def p_set_output(p):
    '''setoutput : OUTPUT LBRACKET INTEGER RBRACKET EQUALS number'''
    p[0] = 'SET', 'OUTPUT', int(p[3]), p[6]


def p_set_input_size(p):
    '''setinputsize : INPUTSIZE number'''
    p[0] = 'INPUT_SIZE', int(p[2])


def p_command_if(p):
    '''ifblock : IF boolean THEN LCURLY program  RCURLY'''
    p[0] = ('IF', p[2], p[5])


def p_command_if_else(p):
    '''ifelseblock : IF boolean THEN LCURLY  program  RCURLY  ELSE  LCURLY  program  RCURLY'''
    p[0] = ('IFELSE', p[2], p[5], p[9])


# FOR statement


# def p_command_for(p):
#     '''command : FOR ID EQUALS expr TO expr optstep'''
#     p[0] = ('FOR', p[2], p[4], p[6], p[7])
#

# def p_command_end(p):
#     '''command : END'''
#     p[0] = ('END',)
#

# RETURN statement


# def p_command_return(p):
#     '''command : RETURN'''
#     p[0] = ('RETURN',)
#

def p_variable(p):
    """variable : ID"""
    p[0] = ('VAR', p[1])


# Builds a list of variable targets as a Python list


# def p_varlist(p):
#     '''varlist : varlist COMMA variable
#                | variable'''
#     if len(p) > 2:
#         p[0] = p[1]
#         p[0].append(p[3])
#     else:
#         p[0] = [p[1]]


# # Builds a list of numbers as a Python list
#

def p_numlist(p):
    '''numlist : numlist COMMA number
               | number'''

    if len(p) > 2:
        p[0] = p[1]
        p[0].append(p[3])
    else:
        p[0] = [p[1]]


# # A number. May be an integer or a float


def p_number(p):
    '''number  : INTEGER
               | FLOAT'''
    p[0] = eval(p[1])


# A signed number.


def p_number_signed(p):
    '''number  : MINUS INTEGER
               | MINUS FLOAT'''
    p[0] = eval("-" + p[2])


def p_boolean(p):
    """boolean  : TRUE
                  | FALSE"""
    p[0] = bool(p[1])


def p_boolean_comparison(p):
    """boolean : variable GT variable
                | variable GE variable
                | variable LE variable
                | variable LT variable
    """
    p[0] = ['CMP', p[1], p[2], p[3]]


def p_boolean_expr(p):
    """boolean : boolean AND boolean
                | boolean OR boolean
                | NOT boolean
    """

    if p[2] in ['and', 'or']:
        p[0] = ['GATE', p[1], p[2], p[3]]
    else:
        p[0] = ['GATE', p[1], p[2]]


def p_error(p):
    print(p)
    if not p:
        print("SYNTAX ERROR AT EOF")


bparser = yacc.yacc()


def parse(data, debug=0):
    bparser.error = 0
    p = bparser.parse(data, debug=debug)
    # print(p)
    if bparser.error:
        return None
    return p
