import copy
import math

from core.integral_bound import calculate_bounds
from core.template import TEMPLATE, EPS_INDEX, K_INDEX, INTEGRAL_INDEX
from sexpdata import dumps, Symbol


def flip_comparison(cmp):
    db = dict(
        (('<=', '>'), ('>=', '<'), ('<', '>='), ('>', '<='))
    )

    return db[cmp]


def handle_set_output(statement, path):
    path['output'][statement[2]] = statement[3]


def get_value_by_index_or_var_name(info, path):
    if info[0] == 'VAR':
        return {'type': 'NUMERIC', 'value': path['variables'][info[1]]['value']}
    if info[0] == 'INDEX':
        return {'type': 'INPUT', 'a': path['input'][0][info[1]], 'b': path['input'][1][info[1]]}


def handle_assignment(statement, path):
    if statement[1] == 'NUMERIC':
        path['variables'][statement[2][1]] = dict(type='NUMERIC', value=statement[3])

    if statement[1] == 'GAUSS':
        path['variables'][statement[2][1]] = dict(type='RANDOM', dist=statement[1], factor=statement[3][0],
                                                  mean=get_value_by_index_or_var_name(statement[3][1], path))


def handle_if(statement, program, index, args, path, paths):
    new_paths = [path]
    path['conditions'].append(statement[1])
    handle_statement(statement[2], 0, args, path, new_paths)
    for _path in new_paths:
        if _path not in paths:
            paths.append(_path)
            handle_statement(program, index + 1, _path, paths)


def handle_else(statement, program, index, args, path, paths):
    new_paths = [path]
    cmp_statement = copy.deepcopy(statement[1])
    cmp_statement[2] = flip_comparison(cmp_statement[2])
    path['conditions'].append(cmp_statement)

    if statement[0] == 'IFELSE':
        handle_statement(statement[3], 0, args, path, new_paths)

    for _path in new_paths:
        paths.append(_path)
        handle_statement(program, index + 1, args, _path, paths)


def handle_statement(program, index, args, path, paths):
    if index >= len(program):
        return

    statement = program[index]

    if statement[0] == 'assignment':
        handle_assignment(statement, path)

    if statement[0] == 'INPUT':
        path['input'] = statement[1], statement[2]

    if statement[0] == 'OUTPUT':
        path['output'] = statement[1]

    if statement[0] == 'IF' or statement[0] == 'IFELSE':
        else_path = copy.deepcopy(path)
        handle_if(statement, program, index, args, path, paths)
        handle_else(statement, program, index, args, else_path, paths)

    if statement[0] == 'SET' and statement[1] == 'OUTPUT':
        handle_set_output(statement, path)

    handle_statement(program, index + 1, args, path, paths)


def get_k_eb_factors(path, lower_eps):
    vars_in_conditions = set()
    sigmas = []

    for condition in path['conditions']:
        vars_in_conditions.add(condition[1][1])
        vars_in_conditions.add(condition[3][1])

        if path['variables'][condition[1][1]]['type'] == 'RANDOM' and path['variables'][condition[1][1]][
            'dist'] == 'GAUSS':
            sigmas.append(
                lower_eps / path['variables'][condition[1][1]]['factor']
            )

        if path['variables'][condition[3][1]]['type'] == 'RANDOM' and path['variables'][condition[3][1]][
            'dist'] == 'GAUSS':
            sigmas.append(
                lower_eps / path['variables'][condition[3][1]]['factor']
            )

    max_sigma = max(sigmas)
    k, eb = calculate_bounds(max_sigma)

    return math.ceil(k), eb, vars_in_conditions


def get_constant_for_gauss(vars, path):
    factor = 1
    for var in vars:
        factor *= path['variables'][var]['factor']

    factor /= math.sqrt(math.pi ** len(vars))

    return [Symbol('/'), factor, [Symbol('pow'), [Symbol('sqrt'), Symbol('eps')], len(vars)]]


def outer_integral(inner_integrals, var, factor):
    template = [Symbol('integral'),
                [Symbol('-'), Symbol('k')], Symbol('k'),
                [Symbol('lambda'), [Symbol(var), Symbol('Real')],
                 [Symbol('*'),
                  [Symbol('exp'),
                   [Symbol('-'),
                    [Symbol('/'),
                     [Symbol('*'), Symbol(var), Symbol(var), Symbol('eps'), Symbol('eps')],
                     [Symbol('*'), 2, factor ** 2]]]]]]]

    for inner_integral in inner_integrals:
        template[3][2].insert(1, inner_integral)

    return template


def inner_integral(factor, input, var, outer_var):
    return [Symbol('integral'),
            [Symbol('-'), input, Symbol('k')],
            Symbol(outer_var),
            [Symbol('lambda'),
             [Symbol(var), Symbol('Real')],
             [Symbol('exp'),
              [Symbol('-'),
               [Symbol('/'),
                [Symbol('*'),
                 [Symbol('-'), Symbol(var), input],
                 [Symbol('-'), Symbol(var), input],
                 Symbol('eps'),
                 Symbol('eps')],
                [Symbol('*'), 2, factor ** 2]]]]]]


def add_error_eb(exp, eb):
    return [Symbol('+'), exp, eb]


def outer_integral_and_constant(outer_integral, constant):
    return [Symbol('*'), constant, outer_integral]


def exp_eps(expression):
    return [Symbol('*'), [Symbol('exp'), Symbol('eps')], expression]


def transform_to_dreal(program, args):
    path = get_required_path(program, args)

    k, eb, vars = get_k_eb_factors(path, args.eps[0])

    dreal_template = copy.deepcopy(TEMPLATE)

    constant_factor = get_constant_for_gauss(vars, path)

    # print(dumps(constant_factor))

    dreal_template[EPS_INDEX][1][2] = args.eps[0]
    dreal_template[EPS_INDEX + 1][1][2] = args.eps[1]
    dreal_template[K_INDEX][1][2] = k

    outer_var = path['conditions'][0][3][1]
    inner_integrals = []
    inner_integrals_adj = []
    for var in vars:
        if var != outer_var:
            # print(path['variables'][var])
            inner_integrals.append(
                inner_integral(
                    path['variables'][var]['factor'],
                    path['variables'][var]['mean']['a'],
                    var,
                    outer_var
                )
            )

            inner_integrals_adj.append(
                inner_integral(
                    path['variables'][var]['factor'],
                    path['variables'][var]['mean']['b'],
                    var,
                    outer_var
                )
            )

    outer = outer_integral(inner_integrals, outer_var, path['variables'][outer_var]['factor'])
    outer_adj = outer_integral(inner_integrals_adj, outer_var, path['variables'][outer_var]['factor'])

    outer_constant = outer_integral_and_constant(outer, constant_factor)
    outer_constant_adj = outer_integral_and_constant(outer_adj, constant_factor)
    outer_constant_adj = exp_eps(outer_constant_adj)
    outer_constant_adj = add_error_eb(outer_constant_adj, eb)

    dreal_template[INTEGRAL_INDEX][1][1].append(outer_constant)
    dreal_template[INTEGRAL_INDEX][1][1].append(outer_constant_adj)

    with open('dreal_output.smt2', 'w+') as f:
        f.write(dumps(dreal_template)[1:-1])


def get_required_path(program, args):
    path = {'variables': dict(), 'input': None, 'output': None, 'conditions': []}

    paths = [path]

    handle_statement(program, 0, args, path, paths)

    output_len = len(path['output'])
    required_output = [0] * output_len
    required_path = None
    for path in paths:
        print(path['output'], path['conditions'])
        if path['output'] == required_output:
            required_path = path
            break

    return required_path
    # return paths
    # return paths
