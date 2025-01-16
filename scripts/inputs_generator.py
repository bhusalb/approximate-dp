import argparse
import json
import os

parser = argparse.ArgumentParser(description='SVT example generator')
parser.add_argument('--number', '-n', type=int, required=True)
args = parser.parse_args()

root_dir = os.path.join(os.path.dirname(__file__), '../')

examples_dir = os.path.join(root_dir, 'examples', 'inputs')

for i in range(1, args.number + 1):
    with open(f'{examples_dir}/inputs_{i}.json', 'w') as f:
        _input = [
            [
                [0] * i, [1] * i,
            ]
        ]
        f.write(json.dumps(_input))
