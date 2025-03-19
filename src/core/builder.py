import copy
from collections import defaultdict

from .graph import build_graph


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

    if statement[1] == 'RANDOM':
        path['variables'][statement[2][1]] = dict(type='RANDOM', dist=statement[3][0], factor=statement[3][1],
                                                  mean=get_value_by_index_or_var_name(statement[3][2], path),
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


def optimize(G, tree, var_map, transpose):
    # Check if the graph has multiple weakly connected components
    components = G.decompose(mode="weak")
    if len(components) > 1:
        return max([optimize(comp, tree, var_map, transpose) for comp in components])

        # If the graph is a single node
    if len(G.vs) == 1:
        if G.vs[0]['var']['type'] == 'RANDOM':
            v = G.vs[0]['name']
            tree[var_map[v]] = dict()
        return 1

        # If the graph has multiple nodes
    source_nodes = [v.index for v in G.vs if G.degree(v.index, mode="out" if transpose else "in") == 0]
    sources = [(G.vs[idx]['name'], G.vs[idx]['var']['type']) for idx in source_nodes]
    G_prime = G.copy()
    G_prime.delete_vertices(source_nodes)
    depth = 0
    for source, source_type in sources:
        if source_type == 'RANDOM':
            v = var_map[source]
            tree[v] = dict()
            tree = tree[v]
            depth += 1

    depth += optimize(G_prime, tree, var_map, transpose)

    return depth


def upper_limit(vertex, eb, transpose, inner):
    conditions = []
    for edge in vertex.out_edges():
        if transpose or edge.target_vertex['var']['type'] == 'NUMERIC':
            conditions.append(edge.target_vertex['var'])

    if len(conditions) == 0:
        if inner:
            return {'type': 'infinity', 'vars': []}, eb + 1
        else:
            return {'type': 'mean', 'mean': vertex['var']['mean'], 'vars': []}, eb

    return {'type': 'variables', 'vars': conditions, 'opr': 'min'}, eb


def lower_limit(vertex, eb, transpose, inner):
    conditions = []
    for edge in vertex.in_edges():
        if not transpose or edge.target_vertex['var']['type'] == 'NUMERIC':
            conditions.append(edge.source_vertex['var'])

    if len(conditions) == 0:
        if inner:
            return {'type': 'infinity', 'vars': []}, eb + 1
        else:
            return {'type': 'mean', 'mean': vertex['var']['mean'], 'vars': []}, eb

    return {'type': 'variables', 'vars': conditions, 'opr': 'max'}, eb


def traverse(subgraph, tree, integrals, transpose):
    eb = {'gaussian': 0, 'laplace': 0}
    for vertex_index in tree:
        vertex = subgraph.vs[vertex_index]
        integral = dict()
        integral['var'] = vertex['var']
        integral['var_name'] = vertex['name']
        integral['inner'] = dict()
        inner_tree = tree[vertex_index]

        integral['upper_limit'], eb1 = upper_limit(vertex, 0, transpose, inner_tree)
        integral['lower_limit'], eb2 = lower_limit(vertex, 0, transpose, inner_tree)

        eb[vertex['var']['dist']] = eb1 + eb2
        if inner_tree:
            integral['inner'] = {
                'opr': 'product',
                'integrals': []
            }
            inner_eb = traverse(subgraph, inner_tree, integral['inner']['integrals'], transpose)
            eb = {key: inner_eb[key] + eb[key] for key in inner_eb.keys()}

        integrals.append(integral)
    return eb


def regular_structure(graph):
    ordering = graph.topological_sorting()
    tree = dict()
    depth = 0
    current_tree = tree
    for vertex in ordering:
        if graph.vs[vertex]['var']['type'] == 'NUMERIC':
            continue
        current_tree[vertex] = dict()
        current_tree = current_tree[vertex]
        depth += 1

    return tree, depth, False


def optimize_structure(graph):
    var_map = dict(map(lambda v: (v['name'], v.index), graph.vs))
    tree = dict()
    depth = optimize(graph, tree, var_map, False)

    tree_transpose = dict()
    depth_transpose = optimize(graph, tree_transpose, var_map, True)

    using_transpose = False
    if not depth <= depth_transpose:
        tree = tree_transpose
        using_transpose = True
        depth = depth_transpose

    return tree, depth, using_transpose


def get_integrals(graph, args):
    # graph = graph.as_undirected()
    expression = {'opr': 'product', 'integrals': []}
    tree, depth, using_transpose = regular_structure(graph) if args.regular else optimize_structure(graph)
    expression['eb'] = traverse(graph, tree, expression['integrals'], using_transpose)
    expression['max_depth'] = depth
    return expression


def build(program, args):
    paths = get_paths(program, args)

    graph = None

    expressions = defaultdict(list)

    depths = []
    variables_counts = []
    conditions_counts = []
    for path in paths:
        graph = build_graph(path)
        variables_counts.append(len(graph.vs))
        conditions_counts.append(len(graph.es))
        if not graph.is_dag():
            continue

        expression = get_integrals(graph, args)
        depths.append(expression['max_depth'])
        expressions[str(path['output'])].append(expression)

    return (list(expressions.values()), list(expressions.keys()), graph, depths,
            len(paths), variables_counts, conditions_counts)


def get_paths(program, args):
    path = {'variables': dict(), 'input': None, 'output': None, 'conditions': []}

    paths = [path]

    handle_statement(program, 0, args, path, paths)

    return paths


def get_required_path(paths):
    pass
