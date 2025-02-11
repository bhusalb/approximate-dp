import os, csv

results1 = os.path.join(os.path.dirname(__file__), '../', 'results', 'result_final_optimal.csv')
results2 = os.path.join(os.path.dirname(__file__), '../', 'results', 'result_nonpriv_optimal.csv')

final = os.path.join(os.path.dirname(__file__), '../', 'results', 'result_optimal.csv')


def read_csv(filename):
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        data = dict()
        for row in reader:
            folder = row['folder']
            test = row['test']
            data[f'{folder}_{test}'] = row
        return data


data1 = read_csv(results1)
data2 = read_csv(results2)

data = []
for key in data1:
    row = data1[key]
    if key in data2:
        row = data2[key]
    data.append(row)

for key in data2:
    if key not in data1:
        data.append(data2[key])

with open(final, 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
