import time
import argparse
import csv
import os
import subprocess
import json
from decimal import *

getcontext().prec = 32


def run_command(command, env):
    start_time = time.time()

    process = subprocess.run(
        command,
        env=env,
        stdout=subprocess.PIPE,
        preexec_fn=os.setsid,
        timeout=10000,
        shell=True)

    execution_time = time.time() - start_time
    return execution_time, process.stdout.decode('utf-8')


def run_multiple_times(command, env, num_times):
    total_time = 0
    valid_attempts = 0
    outputs = []
    for _ in range(num_times):
        execution_time, output = run_command(command, env)
        if execution_time is not None:
            total_time += execution_time
            valid_attempts += 1
            outputs.append(output)

    if valid_attempts > 0:
        average_time = total_time / valid_attempts
        return average_time, outputs
    else:
        return None, None


# parser = argparse.ArgumentParser(description='Benchmarking tool')
# parser.add_argument('--folder', '-f', type=str, required=True)
# parser.add_argument('--input', '-i', action='store_true', required=False, default=False)
#
# args = parser.parse_args()


examples = [
    'svt_3',
    'svt_4',
    'svt_5',
    'svt_6',
    'nmax3'
]

eps_list = [
    0.5,
    0.5,
    0.5,
    0.5,
    0.5
]

# outputs = [
#     [0, 0, 0, 0, 1],
#     [0, 1],
#     [0, 1],
#     [1, 1, 0],
#     [-1]
# ]

assert len(examples) == len(eps_list)
root_dir = os.path.join(os.path.dirname(__file__), '../')

input_dir = os.path.join(root_dir, 'examples', 'dipc_inputs')

main_script = os.path.join(root_dir, 'src', 'main.py')

rows = []

template_svt4 = '''python {main} -f {file_path} -e {eps} -d {delta} --input {input_path} -k 8 --prec 24'''

template = '''python {main} -f {file_path} -e {eps} -d {delta} --input {input_path} -k 8'''
# benchmark_time_template_all_inputs = '''python {main} -f {file_path} -e {eps} -d {delta}'''
characterization_template = '''python {main} -f {file_path} -e {eps} -d {delta} --characterize'''

delta = 0

folder = 'dipc'

with open(f'{root_dir}/results/result_dipc_non.csv', 'a', newline='') as outfile:
    # writer = csv.DictWriter(outfile, rows[0].keys())
    writer = None

    examples_dir = os.path.join(root_dir, 'examples', folder)
    # examples = os.listdir(examples_dir)

    for i, example in enumerate(examples):
        eps = eps_list[i]
        input_path = os.path.join(input_dir, f'{example}.json')
        output = dict(folder=folder, eps=eps, delta=delta, test=example)
        file_path = os.path.join(examples_dir, f'{example}.dip')

        command_args = dict(main=main_script, file_path=file_path, eps=eps, delta=delta)

        _, characterization = run_command(characterization_template.format(**command_args), os.environ.copy())
        characterization = json.loads(characterization)

        output = output | characterization
        # command_args['output'] = (str(outputs[i]).replace(' ', ''))[1:-1]
        command_args['input_path'] = input_path
        if example == 'svt_4':
            command = template_svt4.format(**command_args)
        else:
            command = template.format(**command_args)
        print(command)
        try:
            mean_time, _outputs = run_multiple_times(command, os.environ.copy(), 3)
            output['time'] = mean_time
            output['output'] = _outputs[-1]
        except:
            output[f'time'] = "TIMEOUT"
            output[f'output'] = "N/A"

        print('-------------')
        print(output)
        command_args['input_path'] = input_path

        if not writer:
            writer = csv.DictWriter(outfile, fieldnames=output.keys())
            writer.writeheader()
        writer.writerow(output)

# rows.sort(key=lambda a: a['test'], reverse=False)
