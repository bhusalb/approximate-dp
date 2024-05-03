import argparse

from core.builder import build
from core.our_parser import parse


def read_file(file_name):
    with open(file_name) as fp:
        data = fp.read()
    return data


def get_args():
    parser = argparse.ArgumentParser(description='Approx DP')
    parser.add_argument('--file', '-f', type=str, required=True)
    parser.add_argument('--eps', '-e', type=float, required=True, nargs=2)
    parser.add_argument('--delta', '-d', type=float, required=False)
    parser.add_argument('--engine', type=str, required=False, default='dreal')

    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()

    program = parse(read_file(args.file), 0)

    print(build(program, args))
