import os
from itertools import product
import json

root_dir = os.path.join(os.path.dirname(__file__), '../')

input_dir = os.path.join(root_dir, 'examples', 'dipc_inputs')


def manhattan_distance(vec1, vec2):
    if len(vec1) != len(vec2):
        raise ValueError("Both vectors must be of the same length.")
    return sum(abs(a - b) for a, b in zip(vec1, vec2))


def generate_combinations(n):
    return list(product([-1, 0, 1], repeat=n))


for n in range(1, 5):
    combinations = generate_combinations(n)

    master = []

    for i, combination_i in enumerate(combinations):
        for j, combination_j in enumerate(combinations):
            if i != j and manhattan_distance(combination_i, combination_j) <= 1:
                master.append([combination_i, combination_j])

    fp = open(f'{input_dir}/{n}.json', 'w')
    json.dump(master, fp, indent=4)
