import argparse
import sys

from core.builder import build
from core.our_parser import parse
from core.clang import Clang
from transformers import flint, mathematica


def read_file(file_name):
    with open(file_name) as fp:
        data = fp.read()
    return data


def get_args():
    parser = argparse.ArgumentParser(description='Approx DP')
    parser.add_argument('--file', '-f', type=str, required=True)
    parser.add_argument('--eps', '-e', type=float, required=True)
    parser.add_argument('--delta', '-d', type=float, required=False)
    parser.add_argument('--k', '-k', type=int, required=False, default=4)
    parser.add_argument('--debug', '-dd', action='store_true', required=False, default=False)

    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()

    program = parse(read_file(args.file), 0)

    expressions, paths_output = build(program, args)

    if not args.input_size:
        print("Couldn't find input size")
        sys.exit(0)

    flint.process(expressions, paths_output, args)

    if args.debug:
        mathematica.process(expressions, paths_output, args)

    clang = Clang('gcc', library_dirs=['flint'])
    clang.compile_binary('temp_program.c', 'temp_program')
    clang.output = 'temp_program'
    cagrs = {'eps': args.eps, 'delta': args.delta, 'k': args.k}

    if args.debug:
        cagrs['debug'] = ''

    clang.run(cagrs)
