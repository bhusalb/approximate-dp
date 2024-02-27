import argparse

from core.our_parser import parse


def read_file(file_name):
    with open(file_name) as fp:
        data = fp.read()
    return data


def get_args():
    parser = argparse.ArgumentParser(description='Approx DP')
    parser.add_argument('--file', '-f', type=str, required=True)

    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()

    program = parse(read_file(args.file))

    print(program)
