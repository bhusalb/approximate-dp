import csv
import os

import matplotlib.pyplot as plt

from matplotlib.ticker import MaxNLocator

def read_csv(file):
    fp = open(file, 'r')
    csv_reader = csv.DictReader(fp)

    return list(csv_reader)


root_dir = os.path.join(os.path.dirname(__file__), '../')

result_file = os.path.join(root_dir, 'results', 'result.csv')

data = read_csv(result_file)

inputs_count = []
time_taken = []
for row in data:
    if row['output']:
        number_of_inputs = int(row['test'].split('.')[0].split('_')[1])
        inputs_count.append(number_of_inputs)
        time_taken.append(float(row['time']))


plt.figure()

plt.plot(inputs_count, time_taken)
#plt.legend(loc="upper left")
plt.xlabel("number of inputs")
# plt.xlim(0, int(n_box_rows[-1]['n']))
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

plt.ylabel("time")
plt.title('SVT Performance')

plt.savefig(f'{root_dir}/results/figure-1.png', bbox_inches='tight', dpi=300)