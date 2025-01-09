import copy
import math
from collections import defaultdict

from .graph import build_graph
from .integral_bound import calculate_bounds


def flip_comparison(cmp):
    db = dict(
        (('<=', '>'), ('>=', '<'), ('<', '>='), ('>', '<='))
    )

    return db[cmp]


def handle_set_output(statement, path):
    path['output'][statement[2]] = statement[3]


def get_value_by_index_or_var_name(info, path):
    if type(info) is int:
        return {'type': 'NUMERIC', 'value': info}

    if info[0] == 'VAR':
        return {'type': 'NUMERIC', 'value': path['variables'][info[1]]['value']}
    if info[0] == 'INDEX':
        return {'type': 'INPUT', 'index': info[1]}


def handle_assignment(statement, path):
    if statement[1] == 'NUMERIC':
        path['variables'][statement[2][1]] = dict(type='NUMERIC', value=statement[3], name=statement[2][1])

    if statement[1] == 'GAUSS':
        path['variables'][statement[2][1]] = dict(type='RANDOM', dist=statement[1], factor=statement[3][0],
                                                  mean=get_value_by_index_or_var_name(statement[3][1], path),
                                                  name=statement[2][1])


def handle_if(statement, program, index, args, path, paths):
    new_paths = [path]
    path['conditions'].append(statement[1])
    handle_statement(statement[2], 0, args, path, new_paths)
    for _path in new_paths:
        if _path not in paths:
            paths.append(_path)
            handle_statement(program, index + 1, args, _path, paths)


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

    if statement[0] == 'INPUT_SIZE':
        args.input_size = statement[1]

    handle_statement(program, index + 1, args, path, paths)


def get_k_eb_factors(paths, lower_eps):
    vars_in_conditions = set()
    sigmas = []
    for path in paths:
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

    return math.ceil(k), eb


def upper_limit(vertex, eb):
    conditions = []
    for edge in vertex.out_edges():
        if edge.target_vertex['var']['type'] == 'NUMERIC':
            conditions.append(edge.target_vertex['var'])

    return ({'type': 'infinity', 'vars': []}, eb + 1) if len(conditions) == 0 else (
        {'type': 'variables', 'vars': conditions, 'opr': 'min'}, eb)


def lower_limit(vertex, eb):
    conditions = []
    for edge in vertex.in_edges():
        conditions.append(edge.source_vertex['var'])
    return ({'type': 'infinity', 'vars': []}, eb + 1) if len(conditions) == 0 else (
        {'type': 'variables', 'vars': conditions, 'opr': 'max'}, eb)


def optimize(subgraph, ordering):
    dependencies = dict()

    for i in range(len(ordering)):
        vertex = subgraph.vs[ordering[i]]
        cur_path = []
        for edge in vertex.in_edges():
            cur_path += dependencies[edge.source]
        dependencies[ordering[i]] = list(dict.fromkeys(cur_path)) + [ordering[i]]


    root = dict()

    pointer = dict()

    for path in dependencies.values():
        for_path = root
        for vertex in path:

            if vertex not in pointer:
                for_path[vertex] = dict()
                pointer[vertex] = for_path[vertex]
            else:
                for_path = pointer[vertex]

            # if vertex not in for_path:
            #     for_path[vertex] = dict()

            # for_path = for_path[vertex]

    return root


def get_integrals(graph):
    # graph = graph.as_undirected()
    expression = {'opr': 'product', 'integrals': []}

    sub_graphs = graph.connected_components(mode='weak').subgraphs()
    eb = 0
    for subgraph in sub_graphs:
        ordering = subgraph.topological_sorting()
        new_ordering = []

        # for o_index in ordering:
        #     vertex = subgraph.vs[o_index]
        #     if vertex['var']['type'] == 'NUMERIC':
        #         continue
        #     new_ordering.append(o_index)

        tree = optimize(subgraph, ordering)
        integral = dict()
        expression['integrals'].append(integral)

        visited = []
        for index in ordering:
            vertex = subgraph.vs[index]

            integral['var'] = vertex['var']
            integral['var_name'] = vertex['name']
            integral['upper_limit'], eb = upper_limit(vertex, eb)
            integral['lower_limit'], eb = lower_limit(vertex, eb)
            integral['inner'] = dict()
            integral = integral['inner']
            visited.append(index)
    expression['eb'] = eb
    return expression


def build(program, args):
    paths = get_paths(program, args)

    graph = None

    expressions = defaultdict(list)
    for path in paths:
        graph = build_graph(path)

        if not graph.is_dag():
            continue

        expressions[str(path['output'])].append(get_integrals(graph))

    return list(expressions.values()), list(expressions.keys()), graph


def get_paths(program, args):
    path = {'variables': dict(), 'input': None, 'output': None, 'conditions': []}

    paths = [path]

    handle_statement(program, 0, args, path, paths)

    return paths


def get_required_path(paths):
    pass
