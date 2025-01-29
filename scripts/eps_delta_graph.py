import csv
import os
import argparse
import matplotlib.pyplot as plt

from matplotlib.ticker import MaxNLocator

parser = argparse.ArgumentParser(description='Benchmarking tool')
# parser.add_argument('--type', '-t', type=str, required=True)
parser.add_argument('--all', '-a', action='store_true', required=False, default=False)

type_to_title = {
    r'\AboveThreshold': 'Above Threshold',
    r'\BelowThreshold': 'Below Threshold',
}

type_to_marker = {
    'svt_max': 'o',
    # 'noisy_min': 'Noisy Min',
    # 'noisy_max': 'Noisy Max',
    'svt': '^'
}

delta_to_marker = {
    'svt_max': 'o',
    # 'noisy_min': 'Noisy Min',
    # 'noisy_max': 'Noisy Max',
    'svt': '^'
}

delta_to_linestyle = {
    0.01: '-',
    # 'noisy_min': 'Noisy Min',
    # 'noisy_max': 'Noisy Max',
    0.5: '-.'
}

args = parser.parse_args()


def read_csv(file):
    fp = open(file, 'r')
    csv_reader = csv.DictReader(fp)

    return list(csv_reader)


root_dir = os.path.join(os.path.dirname(__file__), '../')

all_suffix = ''

if args.all:
    all_suffix = '_all'

result_file = os.path.join(root_dir, 'results', f'result_new_scaling.csv')

data = read_csv(result_file)

eps_array = []
time_taken = []
delta_array = []
data = sorted(data, key=lambda row: (float(row['eps']), float(row['delta'])))

new_data = dict()

for row in data:
    if row['type'] not in new_data:
        new_data[row['type']] = dict()

    eps = float(row['eps'])
    delta = float(row['delta'])

    if eps == 20:
        continue

    if delta not in new_data[row['type']]:
        new_data[row['type']][delta] = dict(time=[], eps=[])

    new_data[row['type']][delta]['time'].append(float(row['time']))
    new_data[row['type']][delta]['eps'].append(eps)

for _type in new_data:
    plt.figure()

    for delta in [0.01, 0.5]:
        plt.plot(new_data[_type][delta]['eps'], new_data[_type][delta]['time'], linestyle=delta_to_linestyle[delta],
                 label=r'$\delta' + f'={delta}$')
    # plt.legend(loc="upper left")
    plt.xlabel(r"$\epsilon$")
    # plt.xlim(0, int(n_box_rows[-1]['n']))
    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

    plt.ylabel("Time (seconds)")

    plt.legend()
    plt.title(r'Impact of $\epsilon$ and $\delta$  on Above Threshold')

    plt.savefig(f'{root_dir}/results/eps_delta.png', bbox_inches='tight', dpi=300)
