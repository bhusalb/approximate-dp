import argparse

from core.builder import build
from core.our_parser import parse
from core.clang import Clang
from transformers import transformers

def read_file(file_name):
    with open(file_name) as fp:
        data = fp.read()
    return data


def get_args():
    parser = argparse.ArgumentParser(description='Approx DP')
    parser.add_argument('--file', '-f', type=str, required=True)
    parser.add_argument('--eps', '-e', type=float, required=True)
    parser.add_argument('--input', '-n', type=int, required=True)
    parser.add_argument('--delta', '-d', type=float, required=False)
    parser.add_argument('--debug', '-dd', action='store_true', required=False, default=False)

    parser.add_argument('--engine', type=str, required=False, default='flint')

    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()

    program = parse(read_file(args.file), 0)

    expressions = build(program, args)

    transformers[args.engine](expressions, args)


    clang = Clang('gcc', library_dirs=['flint'])
    clang.compile_binary('temp_program.c', 'temp_program')
    clang.output = 'temp_program'
    cagrs = {'eps': args.eps, 'delta': args.delta, 'n': args.input}

    if args.debug:
        cagrs['debug'] = ''

    clang.run(cagrs)
