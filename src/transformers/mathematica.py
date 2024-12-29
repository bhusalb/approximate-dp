def get_mean(integral, inputs):
    if integral['var']['mean']['type'] == 'NUMERIC':
        return str(integral['var']['mean']['value'])
    else:
        return inputs[integral['var']['mean']['index']]

def get_std(integral):
    return str(integral['var']['factor']) +'/eps'

def get_lower_limit(integral, inputs):
    if integral['lower_limit'][0] != 'max':
        return get_mean(integral, inputs) + f"- k * {get_std(integral)}"
    else:
        if len(integral['lower_limit'][1]) > 1:
            return 'Max[{'+ ','.join(integral['lower_limit'][1])+'}]'
        else:
            return integral['lower_limit'][1][0]
def get_upper_limit(integral, inputs):
    return get_mean(integral, inputs) + f"+ k * {get_std(integral)}"
def get_limits(integral, inputs):
    return "{" + integral['var_name'] + f", {get_lower_limit(integral, inputs)}, {get_upper_limit(integral, inputs)}" +    "}"

def get_inner_integrals(integrals, inputs, args):
    if integrals:
        return '*' + get_integral(integrals, inputs, args)

    return ''
def get_integral(integral, inputs, args):
    template = f'''Integrate[PDF[NormalDistribution[{get_mean(integral, inputs)}, {get_std(integral)}], {integral['var_name']}] {get_inner_integrals(integral['inner'], inputs, args)}, {get_limits(integral, inputs)}]'''
    return template

def get_mathematica_integrals(expression, index, output, args):
    inputs = [f'I{i}' for i in range(args.input_size)]
    func = f'''ComIntegral{index}[{",". join(map(lambda x: x + '_', inputs))}, k_, eps_] = '''
    for expr in expression:
        for integral in expr['integrals']:
            func += get_integral(integral, inputs, args)

    print("Path: ", output)
    print(func)
def process(expressions, path_outputs, args):
    for i in range(len(expressions)):
        get_mathematica_integrals(expressions[i], i, path_outputs[i], args)


