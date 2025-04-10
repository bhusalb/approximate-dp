import argparse
import os


def write_to_file(file_name, program):
    with open(file_name, 'w+') as f:
        f.write(program)


parser = argparse.ArgumentParser(description='SVT example generator')
parser.add_argument('--number', '-n', type=int, required=True)
parser.add_argument('--max', action='store_true', required=False)

args = parser.parse_args()

sign = '<'

if args.max:
    sign = '>'


def get_for_if_block(i, n):
#     if (not args.max and i == 0):
#         line1 = '''
# NUMERIC Q{{INDEX}} = 1;
#         '''
#     elif args.max and i == n - 1:
#         line1 = '''
# NUMERIC Q{{INDEX}} = 2;
#         '''
#     else:
    template = '''
    RANDOM Q{{INDEX}} = gauss(eps/0.1, INPUT[{{INDEX}}]);
    IF Q{{INDEX}} {{SIGN}} TH THEN {
        OUTPUT[{{INDEX}}] = 1;
    }'''

    template = template.replace('{{INDEX}}', str(i))
    template = template.replace('{{SIGN}}', sign)

    return template


def get_initial_block(n):
    return f'''
INPUTSIZE {n};
NUMERIC TH = 0;
OUTPUT = [{','.join(['0'] * n)}];
    '''


def get_if_and_else_block(start, n, initial_n):
    if n <= 0:
        return ''

    if n == 1:
        return get_for_if_block(start - 1, initial_n)

    template = get_for_if_block(start - n, initial_n) + 'ELSE {' + f'''
        {get_if_and_else_block(start, n - 1, initial_n)}
''' + '}'

    return template


root_dir = os.path.join(os.path.dirname(__file__), '../')

examples_dir = os.path.join(root_dir, 'examples', 'new_nonpriv_svt' + ("_max" if args.max else ''))

for i in range(2, args.number + 1):
    initial_block = get_initial_block(i)
    if_else_block = get_if_and_else_block(i, i, i)
    write_to_file(f'{examples_dir}/example_{i}.dip', initial_block + if_else_block)
