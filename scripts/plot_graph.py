import csv
import os
import argparse
import matplotlib.pyplot as plt

from matplotlib.ticker import MaxNLocator

parser = argparse.ArgumentParser(description='Benchmarking tool')
parser.add_argument('--type', '-t', type=str, required=True)
parser.add_argument('--all', '-a', action='store_true', required=False, default=False)

type_to_title = {
    'svt': 'SVT',
    'noisy_min': 'Noisy Min',
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

result_file = os.path.join(root_dir, 'results', f'result_{args.type}{all_suffix}.csv')

data = read_csv(result_file)

inputs_count = []
time_taken = []

data = sorted(data, key=lambda row: int(row['test'].split('.')[0].split('_')[1]))

for row in data:
    if row['output']:
        number_of_inputs = int(row['test'].split('.')[0].split('_')[1])
        try:
            time_taken.append(float(row['time']))
            inputs_count.append(number_of_inputs)
        except ValueError:
            pass

plt.figure()

plt.plot(inputs_count, time_taken)
# plt.legend(loc="upper left")
plt.xlabel("number of inputs")
# plt.xlim(0, int(n_box_rows[-1]['n']))
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

plt.ylabel("time (seconds)")

all_text = 'Single Pair'
if args.all:
    all_text = 'All Pairs'

plt.title(f'{type_to_title[args.type]} Performance ({all_text})')

plt.savefig(f'{root_dir}/results/{args.type}{all_suffix}.png', bbox_inches='tight', dpi=300)
