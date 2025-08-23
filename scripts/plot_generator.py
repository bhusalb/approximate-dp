import csv
import os
import argparse
import matplotlib.pyplot as plt

from matplotlib.ticker import MaxNLocator

plt.rcParams.update({
    # "text.usetex": True,
    "font.family": "sans-serif"
})
parser = argparse.ArgumentParser(description='Benchmarking tool')
# parser.add_argument('--type', '-t', type=str, required=True)
parser.add_argument('--all', '-a', action='store_true', required=False, default=False)

type_to_title = {
    'svt_max': r'$\text{SVT-Gauss}$',
    'svt_laplace_max': r'$\text{SVT-Laplace}$',
    'svt_mix1_max': r'$\text{SVT-Mix1}$',
}

type_to_marker = {
    'svt_mix1_max': 'o',
    'svt_laplace_max': '^',
    'svt_max': '^'
}

type_to_linestyle = {
    'svt_max': '-.',
    'svt_mix1_max': '--',
    'svt_laplace_max': '-.',
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

folders = ['svt_laplace_max', 'svt_mix1_max', 'svt_max', ]

data = read_csv(os.path.join(root_dir, 'results', f'optimized_data.csv'))
for folder in folders:

    filtered_data = [row for row in data if row['folder'] == folder]

    inputs_count = []
    time_taken = []

    filtered_data = sorted(filtered_data, key=lambda row: int(row['input_size']))

    for row in filtered_data:
        if row['output_single']:
            number_of_inputs = int(row['input_size'])
            try:
                time_taken.append(float(row['time_single']))
                inputs_count.append(number_of_inputs)
            except ValueError:
                pass

    # plt.figure()

    plt.plot(inputs_count, time_taken, label=type_to_title[folder], marker=type_to_marker[folder], linestyle=type_to_linestyle[folder])
    plt.legend(loc="upper left")
    plt.xlabel("$N$")
    # plt.xlim(0, int(n_box_rows[-1]['n']))
    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

    plt.ylabel("Time (seconds)")

    # plt.legend()
    plt.title(f'Impact of Input Size')

plt.savefig(f'{root_dir}/results/graph.png', bbox_inches='tight', dpi=500)
