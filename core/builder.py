import copy
import math

from core.integral_bound import calculate_bounds
from transformers import transformers


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
                path['variables'][condition[1][1]]['factor'] / lower_eps
            )

        if path['variables'][condition[3][1]]['type'] == 'RANDOM' and path['variables'][condition[3][1]][
            'dist'] == 'GAUSS':
            sigmas.append(
                path['variables'][condition[3][1]]['factor'] / lower_eps
            )

    max_sigma = max(sigmas)
    k, eb = calculate_bounds(max_sigma)

    return math.ceil(k), eb, vars_in_conditions


def get_condition_dict(conditions, vars):
    mydict = dict()
    n = len(conditions)
    for var in vars:
        mydict[var] = []
        for i in range(n):
            if var == conditions[i][1][1] or var == conditions[i][3][1]:
                mydict[var].append(i)

    return mydict


def inner_integral(conditions_dict, conditions, visited, var):
    inner = []
    for c_index in conditions_dict[var]:
        if c_index in visited:
            continue
        visited.append(c_index)

        condition = conditions[c_index]
        operator = condition[2]
        a = condition[1][1]
        b = condition[3][1]
        inner_dict = None
        if a == var:
            if operator == '<' or operator == '<=':
                inner_dict = {'var': b, 'upper_limit': var, 'lower_limit': '-k',
                              'inner': inner_integral(conditions_dict, conditions, visited, b)}
            if operator == '>' or operator == '>=':
                inner_dict = {'var': b, 'upper_limit': 'k', 'lower_limit': var,
                              'inner': inner_integral(conditions_dict, conditions, visited, b)}

        if b == var:
            if operator == '<' or operator == '<=':
                inner_dict = {'var': a, 'upper_limit': 'k', 'lower_limit': var,
                              'inner': inner_integral(conditions_dict, conditions, visited, a)}
            if operator == '>' or operator == '>=':
                inner_dict = {'var': a, 'upper_limit': var, 'lower_limit': '-k',
                              'inner': inner_integral(conditions_dict, conditions, visited, a)}

        if inner_dict:
            inner.append(inner_dict)

    return inner


def get_integrals(conditions, vars):
    integrals = []
    conditions_dict = get_condition_dict(conditions, vars)
    sorted_vars = sorted(conditions_dict.keys(), key=lambda k: len(conditions_dict[k]), reverse=True)
    visited = []

    for var in sorted_vars:
        inner = inner_integral(conditions_dict, conditions, visited, var)
        if inner:
            integrals.append({'var': var, 'upper_limit': 'k', 'lower_limit': '-k', 'inner': inner})

    return integrals


def build(program, args):
    path = get_required_path(program, args)

    k, eb, vars = get_k_eb_factors(path, args.eps[0])

    integrals = get_integrals(path['conditions'], vars)

    transformers[args.engine](integrals, k, eb, path['variables'], args)


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
