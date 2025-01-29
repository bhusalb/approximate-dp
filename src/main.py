import argparse
import sys
from statistics import mean

from core.builder import build
from core.graph import plot
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
    parser.add_argument('--input', '-i', type=str, required=False, default=None)
    parser.add_argument('--debug', '-dd', action='store_true', required=False, default=False)
    parser.add_argument('--characterize', '-c', action='store_true', required=False, default=False)
    parser.add_argument('--regular', '-r', action='store_true', required=False, default=False)

    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()

    program = parse(read_file(args.file), 0)

    if args.input:
        args.input = read_file(args.input)

    expressions, paths_output, graph, depths, paths_count, variables_counts, conditions_counts = build(program, args)

    if args.characterize:
        import json

        print(json.dumps({
            "max_depth": max(depths),
            "avg_depth": mean(depths),
            "min_depth": min(depths),
            "max_variables": max(variables_counts),
            "avg_variables": mean(variables_counts),
            "min_variables": min(variables_counts),
            "number_of_paths": paths_count,
            "number_of_outputs": len(paths_output),
            "max_conditions": max(conditions_counts),
            "avg_conditions": mean(conditions_counts),
            "min_conditions": min(conditions_counts),
        }))

        sys.exit(0)

    if not args.input_size:
        print("Couldn't find input size")
        sys.exit(0)

    flint.process(expressions, paths_output, args)

    if args.debug:
        # plot(graph)
        # mathematica.process(expressions, paths_output, args)
        pass
    clang = Clang('gcc', library_dirs=['flint'])
    clang.compile_binary('temp_program.c', 'temp_program')
    clang.output = 'temp_program'
    cagrs = {'eps': args.eps, 'delta': args.delta, 'k': args.k}

    if args.debug:
        cagrs['debug'] = ''

    clang.run(cagrs)
