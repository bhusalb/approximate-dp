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
    'svt_max': r'$\text{SVT-Gauss-Le}$',
    'svt_laplace_max': r'$\text{SVT-Laplace-Le}$',
    'svt_laplace': r'$\text{SVT-Laplace}$',
    # 'noisy_min': 'Noisy Min',
    # 'noisy_max': 'Noisy Max',
    'svt': r'$\text{SVT-Gauss}$',
    'svt_mix1': r'$\text{SVT-Mix1}$',
    'svt_mix2': r'$\text{SVT-Mix2}$',
}

type_to_marker = {
    'svt_mix2': 'o',
    'svt_mix1': 'o',
    'svt_laplace': '^',

    # 'noisy_min': 'Noisy Min',
    # 'noisy_max': 'Noisy Max',
    'svt': '^'
}

type_to_linestyle = {
    'svt_mix2': '-',
    # 'noisy_min': 'Noisy Min',
    # 'noisy_max': 'Noisy Max',
    'svt': '-.',
    'svt_mix1': '--',
    'svt_laplace': '-.',
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

folders = ['svt_laplace', 'svt_mix1', 'svt', ]

data = read_csv(os.path.join(root_dir, 'results', f'new_all_data.csv'))
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

    plt.plot(inputs_count, time_taken, label=type_to_title[folder], linestyle=type_to_linestyle[folder],
             marker=type_to_marker[folder])
    # plt.legend(loc="upper left")
    plt.xlabel("$N$")
    # plt.xlim(0, int(n_box_rows[-1]['n']))
    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

    plt.ylabel("Time (seconds)")

    plt.legend()
    plt.title(f'Impact of Input Size')

plt.savefig(f'{root_dir}/results/svt_plot.png', bbox_inches='tight', dpi=500)
