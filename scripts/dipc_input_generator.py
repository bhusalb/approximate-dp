import os
from itertools import product
import json

root_dir = os.path.join(os.path.dirname(__file__), '../')

input_dir = os.path.join(root_dir, 'examples', 'dipc_inputs')


def generate_combinations(n):
    return list(product([-1, 0, 1], repeat=n))


for n in range(1, 7):
    combinations = generate_combinations(n)

    master = []

    for i, combination_i in enumerate(combinations):
        for j, combination_j in enumerate(combinations):
            if i != j:
                master.append([combination_i, combination_j])

    fp = open(f'{input_dir}/{n}.json', 'w')
    json.dump(master, fp, indent=4)
