import csv
import os

root_dir = os.path.join(os.path.dirname(__file__), '../')
results_dir = os.path.join(root_dir, 'results')

type_to_title = {
    'svt': r'\AboveThreshold',
    'svt_max': r'\BelowThreshold',
    'noisy_min': r'\NoisyMin',
    'noisy_max': r'\NoisyMax',
    'nonpriv_svt': r'\NonPrivAboveThreshold',
    'nonpriv_svt_max': r'\NonPrivBelowThreshold'
}


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
                row[field] = round(float(row[field]), 2)

        if field in ['avg_conditions', ] and field in row:
            row[field] = round(float(row[field]), 2)

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

    if field in ['time_single', 'avg_conditions', 'avg_depth']:
        return round(float(value), 2)

    return value


master = read_csv(os.path.join(results_dir, f'result_optimal.csv'))

interesting_fields = ['type', 'input_size', 'number_of_paths',
                      'avg_conditions', 'output_single', 'time_single', 'output_all', 'time_all', ]

fp = open(os.path.join(results_dir, f'table_1.csv'), 'w')

writer = csv.DictWriter(fp, fieldnames=interesting_fields)
writer.writeheader()

master_rows = []
for key in master:
    row = master[key]
    if row['folder'].startswith('svt'):
        if not (row['input_size'] in [1, 2, 3, 5, 23, 25] or row['input_size'] % 4 == 0):
            continue

    master_rows.append(format_row(row, interesting_fields))

master_rows = sorted(master_rows, key=lambda x: (x['type'], x['input_size']))
writer.writerows(master_rows)

regular_data = read_csv(os.path.join(results_dir, f'result_unoptimized.csv'))
table_2_rows = []
table_2_fields = ['type', 'input_size', ]

mix_fields = ['time_single', 'max_depth', 'avg_depth']
combined_fields = []
for field in mix_fields:
    for _type in ['unoptimize', 'optimize']:
        combined_field = f'{_type}-{field}'
        combined_fields.append(combined_field)

for key in regular_data:
    raw_row = dict(unoptimize=regular_data[key], optimize=master[key])
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

table_3_required_fields = ['delta', 'eps', 'time']
with open(os.path.join(results_dir, f'result_scaling.csv'), 'r') as f:
    reader = csv.DictReader(f)

    for row in reader:
        row = format_row_new(row)
        new_dict = get_required_fields(row, table_3_required_fields)
        new_dict['time'] = format_field(new_dict['time'], 'time')

        # if float(new_dict['eps']) not in [0.1, 1, 10, 15, 20, 25, 30]:
        #     continue
        #
        # if float(new_dict['delta']) not in [0.01, 0.1, 0.5]:
        #     continue
        table_3_rows.append(new_dict)

table_3_rows = sorted(table_3_rows, key=lambda r: (float(r['delta']), float(r['eps'])))
with open(os.path.join(results_dir, f'table_3.csv'), 'w') as fp:
    writer = csv.DictWriter(fp, fieldnames=table_3_required_fields)
    writer.writeheader()
    writer.writerows(table_3_rows)
