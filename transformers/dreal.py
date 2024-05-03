from sexpdata import Symbol, dumps


def add_two_expressions(a, b):
    return [Symbol('+'), a, b]


def subtract(*args):
    return [Symbol('-'), *args]


def multiply_expressions(*args):
    return [Symbol('*'), *args]


def exp_eps(expression):
    return [Symbol('*'), [Symbol('exp'), Symbol('eps')], expression]


def integral_expr(upper, lower, var, expr):
    return [Symbol('integral'),
            lower, upper,
            [Symbol('lambda'), [Symbol(var), Symbol('Real')], expr]]


def gauss_pdf(var, mu, sigma):
    return [Symbol('/'), [Symbol('exp'),
                          [Symbol('/'),
                           [Symbol('-'), [Symbol('pow'), [Symbol('/'), [Symbol('-'), Symbol(var), mu], sigma], 2]],
                           2]], [Symbol('*'), sigma, [Symbol('sqrt'), [Symbol('*'), 2, Symbol('pi')]]]]


def translate_limit(limit, mu):
    if limit in ['k', '-k']:
        if limit == 'k':
            return [Symbol('+'), mu, Symbol('k')]
        else:
            return [Symbol('-'), mu, Symbol('k')]

    return Symbol(limit)


def set_eps(args):
    return [
        [Symbol('assert'), [Symbol('>='), Symbol('eps'), args.eps[0]]],
        [Symbol('assert'), [Symbol('<='), Symbol('eps'), args.eps[1]]]
    ]


def set_k(k):
    return [
        [Symbol('assert'), [Symbol('='), Symbol('k'), k]],
    ]


def compare_two(pro, pro_adjacent):
    return [[Symbol('assert'), [Symbol('not'), [Symbol('<='), pro, pro_adjacent]]]]


def boiler_plate(program):
    return [[Symbol('set-logic'), Symbol('QF_NRA')], [Symbol('declare-fun'), Symbol('pi'), [], Symbol('Real')],
            [Symbol('assert'), [Symbol('>='), Symbol('pi'), 3.141592653589793]],
            [Symbol('assert'), [Symbol('<='), Symbol('pi'), 3.141592653589793]],
            [Symbol('declare-fun'), Symbol('eps'), [], Symbol('Real')],
            [Symbol('declare-fun'), Symbol('k'), [], Symbol('Real')],
            *program,
            [Symbol('check-sat')], [Symbol('exit')]]


def write_to_file(file_name, program):
    with open(file_name, 'w+') as f:
        f.write(dumps(boiler_plate(program))[1:-1])


def process_integral(integral, vars, use_adj=False):
    mu = None
    var = integral['var']
    sigma = [Symbol('/'), vars[var]['factor'], Symbol('eps')]
    if vars[var]['mean']['type'] == 'INPUT':
        if use_adj:
            mu = vars[var]['mean']['b']
        else:
            mu = vars[var]['mean']['a']
    else:
        mu = vars[var]['mean']['value']

    pdf = gauss_pdf(integral['var'], mu, sigma)

    prd = []

    for inner in integral['inner']:
        prd.append(process_integral(inner, vars, use_adj))

    if prd:
        expr = multiply_expressions(pdf, *prd)
    else:
        expr = pdf

    return integral_expr(translate_limit(integral['upper_limit'], mu), translate_limit(integral['lower_limit'], mu),
                         var, expr)


def process(integrals, k, eb, vars, args):
    prd = []
    prd_adj = []
    for integral in integrals:
        prd.append(process_integral(integral, vars))
        prd_adj.append(process_integral(integral, vars, True))

    len_of_prd = len(prd)
    if len_of_prd == 1:
        prd = prd[0]
        prd_adj = prd_adj[0]
    else:
        prd = multiply_expressions(*prd)
        prd_adj = multiply_expressions(*prd_adj)

    prd_adj = exp_eps(prd_adj)

    if args.delta:
        prd_adj = add_two_expressions(prd_adj, args.delta)

    prd = add_two_expressions(prd, multiply_expressions(len_of_prd, eb))

    prg = [
        *set_eps(args),
        *set_k(k),
        *compare_two(prd, prd_adj)
    ]

    return write_to_file('.'.join(args.file.split('.')[:-1] + ['smt2']), prg)
