import math


def get_mean(integral, inputs):
    if integral['var']['mean']['type'] == 'NUMERIC':
        return str(integral['var']['mean']['value'])
    else:
        return inputs[integral['var']['mean']['index']]


def get_std(integral):
    return str(integral['var']['factor']) + '/eps'


def get_mean_value(var, inputs):
    if var['type'] == 'INPUT':
        return inputs[var['index']]

    if var['type'] == 'NUMERIC':
        return var['value']

    raise Exception('Unsupported mean value')


def get_vars(vars):
    return ','.join([var['name'] if var['type'] == 'RANDOM' else var['value'] for var in vars])


def _get_limit(_type, limit, inputs, integral, args):
    sign = {
        'upper': '+',
        'lower': '-'
    }

    opr = {
        'upper': 'Min',
        'lower': 'Max'
    }

    if limit['type'] == 'mean':
        return get_mean_value(limit['mean'], inputs), True
    if limit['type'] == 'variables':
        if len(limit['vars']) == 1:
            return get_vars(limit['vars']), False
        return opr[_type] + '[{' + get_vars(limit['vars']) + '}]', False
    if limit['type'] == 'infinity':
        return get_mean(integral, inputs) + sign[_type] + 'k*' + get_std(integral), False

    raise Exception('error to compute limit')


def get_lower_limit(integral, inputs, args):
    return _get_limit('lower', integral['lower_limit'], inputs, integral, args)


def get_upper_limit(integral, inputs, args):
    return _get_limit('upper', integral['upper_limit'], inputs, integral, args)


def get_limits(integral, inputs, args):
    lower_limit, half1 = get_lower_limit(integral, inputs, args)
    upper_limit, half2 = get_upper_limit(integral, inputs, args)
    return "{" + integral[
        'var_name'] + f", {lower_limit}, {upper_limit}" + "}", half1 or half2


def get_inner_integrals(expr, inputs, args):
    if expr:
        return '*' + ('*'.join([get_integral(integral, inputs, args) for integral in expr['integrals']]))

    return ''


def get_integral(integral, inputs, args):
    limit, add_half = get_limits(integral, inputs, args)
    dist = 'NormalDistribution' if integral['var']['dist'] == 'gaussian' else 'LaplaceDistribution'
    integral_template = f'''Integrate[PDF[{dist}[{get_mean(integral, inputs)}, {get_std(integral)}], {integral['var_name']}] {get_inner_integrals(integral['inner'], inputs, args)}, {limit}]'''

    if add_half:
        integral_template = '(0.5 +' + integral_template + ')'

    return integral_template


def gaussian_error_bound():
    # return math.exp(-((k ** 2) / 2))
    return 'Exp[-(k ^ 2) / 2]'


def laplace_error_bound():
    # return math.exp(-k) / 2
    return 'Exp[-k] / 2'


def get_error_bound(eb, args):
    return (str(eb['gaussian']) + ' * ' + gaussian_error_bound()) + "+" + (
            str(eb['laplace']) + '*' + laplace_error_bound())


def get_for_a_expression(expr, inputs, args):
    return '*'.join([get_integral(integral, inputs, args) for integral in expr['integrals']]) + '+' + get_error_bound(
        expr['eb'], args)


def get_for_a_output(expressions, index, output, args):
    inputs = [f'I{i}' for i in range(args.input_size)]
    func = f'''ComIntegral{index}[{",".join(map(lambda x: x + '_', inputs))}, k_, eps_] = ''' + '+'.join(
        [get_for_a_expression(expression, inputs, args) for expression in expressions]
    )
    # for expr in expression:
    #     for integral in expr['integrals']:
    #         func += get_integral(integral, inputs, args)

    print("Path: ", output)
    print(func)


def process(expressions, path_outputs, args):
    for i in range(len(expressions)):
        get_for_a_output(expressions[i], i, path_outputs[i], args)
