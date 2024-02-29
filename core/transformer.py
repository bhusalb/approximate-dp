import copy


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


def transform_to_dreal(path, args):
    pass



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
            required_output = path
            break

    # return paths
    # return paths


