import csv
import os

root_dir = os.path.join(os.path.dirname(__file__), '../')
results_dir = os.path.join(root_dir, 'results')

type_to_title = {
    'svt': r'\AboveThreshold',
    'svt_max': r'\BelowThreshold',
    'noisy_min': r'\NoisyMinGauss',
    'noisy_max': r'\NoisyMaxGauss',
    'nonpriv_svt': r'\NonPrivAboveThresholdTwo',
    'nonpriv_svt_max': r'\NonPrivBelowThresholdTwo',
    'kminmax': r'\kminmax',
    'svt_mix1': r'\MixOneAboveThreshold',
    'svt_mix2': r'\MixTwoAboveThreshold',
    'mrange': r'\mRange',
    'svt_laplace': r'\LaplaceAboveThreshold',
    'svt_laplace_max': r'\LaplaceBelowThreshold',
    'svt_mix1_max': r'\MixOneBelowThreshold',
    'svt_mix2_max': r'\MixTwoBelowThreshold',
    'svt_3': r'\NonPrivBelowThresholdLaplace-$3$',
    'svt_4': r'\NonPrivBelowThresholdLaplace-$4$',
    'svt_5': r'\NonPrivBelowThresholdLaplace-$5$',
    'svt_6': r'\NonPrivBelowThresholdLaplace-$6$',
    'nmax3': r'\NoisyMax-$7$',
    'noisy_min_laplace': r'\LaplaceNoisyMin',
    'noisy_max_laplace': r'\LaplaceNoisyMax',
    'new_nonpriv_svt_max': r'\NonPrivBelowThresholdOne',
    'new_nonpriv_svt': r'\NonPrivAboveThresholdOne',
    'kminmax_laplace': r'\LaplaceKminmax',
    'mrange_laplace': r'\LaplaceMrange',
}

title_to_folder = dict()

for k, v in type_to_title.items():
    title_to_folder[v] = k

examples_to_include = {
    'svt': [2, 5, 25],
    'svt_max': [2, 5, 25],
    'noisy_min': [2, 3, 4],
    'noisy_max': [2, 3, 4],
    'nonpriv_svt': [3, 6],
    'nonpriv_svt_max': [3, 6],
    'kminmax': [3, 4],
    'svt_mix1': [2, 5, 17],
    'svt_mix2': [2, 5, 10],
    'mrange': [1, 2, 3],
    'svt_laplace': [2, 5, 11],
    'svt_laplace_max': [2, 5, 11],
    'svt_mix1_max': [2, 5, 17],
    'svt_mix2_max': [2, 5, 10],
    'noisy_min_laplace': [3, 4],
    'noisy_max_laplace': [3, 4],
    'new_nonpriv_svt_max': [5, 6],
    'new_nonpriv_svt': [5, 6],
}

table_1_order = [
    'svt_max', 'new_nonpriv_svt_max', 'nonpriv_svt_max',
    'svt_mix1_max',
    'noisy_max', 'noisy_min',
    'mrange', 'kminmax',
]

examples_to_include_table2 = [
    'svt_max', 'svt_mix1_max', 'noisy_max'
]


def get_required_fields(data, required_fields):
    return {k: data[k] for k in required_fields if k in data}


def format_row(row, required_fields):
    for field in required_fields:

        if 'time' in field and field in row:
            if row[field] == 'TIMEOUT':
                row[field] = r'$\timeout$'
            elif row[field] == '-' or row[field] == '$-$':
                row[field] = r'$-$'
            else:
                row[field] = round(float(row[field]), 1)

        if field in ['avg_conditions', 'avg_depth'] and field in row:
            row[field] = round(float(row[field]), 1)

    return get_required_fields(row, required_fields)


def format_row_new(row, _type=None):
    if 'input_size' in row:
        row['input_size'] = int(row['input_size'])

    if _type:
        row['type'] = type_to_title[_type]

    for output in ['output', 'output_single', 'output_all']:
        if output in row:
            if row[output] == '{ "DP": 1}':
                row[output] = r'$\checkmark$'
            elif row[output] == 'N/A':
                row[output] = r'$\na$'
            elif row[output] == '{ "DP": -1}':
                row[output] = r'$\times$'
            elif row[output] == '{ "DP": 0}':
                row[output] = r'$\tableunresolved$'
            elif not row[output]:
                row[output] = r'$\experimenterror$'
                time = 'time'
                if '_' in output:
                    suffix = output.rsplit('_', 1)[-1]
                    time = f'{time}_{suffix}'
                row[time] = '$-$'
    return row


def read_csv(p, _type=None):
    fp = open(p, 'r')
    reader = csv.DictReader(fp)
    data = dict()
    for row in reader:
        row = format_row_new(row, row['folder'] if 'folder' in row else None)
        data[row['type'] + '_' + row['test']] = row
    return data


def format_field(value, field):
    if field == 'time_single' and value in ['TIMEOUT', r'$\timeout$']:
        return r'$\timeout$'

    if field in ['time_single', 'avg_conditions', 'avg_depth', 'time']:
        return round(float(value), 2)

    return value


master = read_csv(os.path.join(results_dir, f'optimized_data.csv'))

interesting_fields = ['type', 'input_size', 'number_of_paths',
                      'avg_conditions', 'avg_depth', 'output_single', 'time_single', 'output_all', 'time_all', ]

fp = open(os.path.join(results_dir, f'table_1.csv'), 'w')

writer = csv.DictWriter(fp, fieldnames=interesting_fields)
writer.writeheader()

master_rows = []
for key in master:
    row = master[key]
    if row['folder'] not in examples_to_include or row['folder'] not in table_1_order or not (row['input_size'] in examples_to_include[row['folder']]):
        continue

    master_rows.append(format_row(row, interesting_fields))

master_rows = sorted(master_rows, key=lambda x: (table_1_order.index(title_to_folder[x['type']]), x['input_size']))
writer.writerows(master_rows)

regular_data = read_csv(os.path.join(results_dir, f'unoptimized_data.csv'))
table_2_rows = []
table_2_fields = ['type', 'input_size', ]

mix_fields = ['max_depth', 'avg_depth', 'time_single']
combined_fields = []
for _type in ['unoptimize', 'optimize']:
    for field in mix_fields:
        combined_field = f'{_type}-{field}'
        combined_fields.append(combined_field)

for key in regular_data:
    raw_row = dict(unoptimize=regular_data[key], optimize=master[key])

    if raw_row['unoptimize']['folder'] not in examples_to_include_table2:
        continue

    row = get_required_fields(master[key], table_2_fields)
    for field in mix_fields:
        for _type in ['unoptimize', 'optimize']:
            combined_field = f'{_type}-{field}'
            row[combined_field] = format_field(raw_row[_type][field], field)
    table_2_rows.append(row)

table_2_rows = sorted(table_2_rows, key=lambda k: (k['type'], k['input_size']))
fp = open(os.path.join(results_dir, f'table_2.csv'), 'w')
writer = csv.DictWriter(fp, fieldnames=table_2_fields + combined_fields)
writer.writeheader()
writer.writerows(table_2_rows)

table_3_rows = []
table_3_required_fields = ['type', 'input_size', 'eps', 'time', 'output']

input_size_mapping = {
    'svt_4': 2,
    'svt_5': 2,
    'svt_6': 3
}

laplace_file_path = os.path.join(results_dir, f'laplace_data.csv')
if os.path.exists(laplace_file_path):
    with open(laplace_file_path, 'r') as f:
        reader = csv.DictReader(f)

        for row in reader:
            if row['folder'] == 'dipc':
                folder = row['test']
                row['input_size'] = input_size_mapping[folder]
            else:
                folder = row['folder']
                row['input_size'] = row['test'].split('_')[1]

            row = format_row_new(row, folder)
            row['time'] = int(format_field(row['time'], 'time'))
            new_dict = get_required_fields(row, table_3_required_fields)
            table_3_rows.append(new_dict)

    table_3_rows = sorted(table_3_rows, key=lambda r: (r['type'], r['input_size']))
    with open(os.path.join(results_dir, f'table_3.csv'), 'w') as fp:
        writer = csv.DictWriter(fp, fieldnames=table_3_required_fields)
        writer.writeheader()
        writer.writerows(table_3_rows)
