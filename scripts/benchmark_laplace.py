import signal
import time
import argparse
import csv
import os
import subprocess
import json
from decimal import *

import psutil

getcontext().prec = 32


def kill_process_by_name(process_name):
    for proc in psutil.process_iter(attrs=['pid', 'name']):
        if proc.info['name'] == process_name:
            try:
                os.kill(proc.info['pid'], signal.SIGTERM)  # Use SIGKILL if needed
                print(f"Killed process {process_name} with PID {proc.info['pid']}")
            except Exception as e:
                print(f"Error killing process {process_name}: {e}")


def run_command(command, env):
    start_time = time.time()

    process = subprocess.run(
        command,
        env=env,
        stdout=subprocess.PIPE,
        preexec_fn=os.setsid,
        timeout=20000,
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

examples = {
    'svt_laplace_max': {
        'example_1': {
            'input_size': 1,
            'eps': [0.5, ]
        },
        'example_2': {
            'input_size': 2,
            'eps': [0.5, ]
        },
        'example_3': {
            'input_size': 3,
            'eps': [0.5, ]
        },
        'example_4': {
            'input_size': 4,
            'eps': [0.5, ]
        }
    },
    'noisy_max_laplace': {
        'example_3': {
            'input_size': 3,
            'eps': [0.5, 1]
        },
    },
    'noisy_min_laplace': {
        'example_3': {
            'input_size': 3,
            'eps': [0.5, 1]
        },
    },
    'dipc': {
        'svt_4': {
            'input_size': 2,
            'eps': [1, ]
        },
        'svt_5': {
            'input_size': 2,
            'eps': [0.5, ]
        },
        'svt_6': {
            'input_size': 3,
            'eps': [1, ]
        },
    },
}

root_dir = os.path.join(os.path.dirname(__file__), '../')

input_dir = os.path.join(root_dir, 'examples', 'dipc_inputs')

main_script = os.path.join(root_dir, 'src', 'main.py')

rows = []

template_svt4 = '''python {main} -f {file_path} -e {eps} -d {delta} --input {input_path} -k 8 --prec 24'''

template = '''python {main} -f {file_path} -e {eps} -d {delta} --input {input_path} -k 8'''
characterization_template = '''python {main} -f {file_path} -e {eps} -d {delta} --characterize'''

delta = 0

with open(f'{root_dir}/results/laplace_data.csv', 'a', newline='') as outfile:
    writer = None
    for folder in examples:
        examples_dir = os.path.join(root_dir, 'examples', folder)

        for example in examples[folder]:
            input_size = examples[folder][example]['input_size']
            eps_list = examples[folder][example]['eps']
            for eps in eps_list:
                if folder == 'dipc':
                    input_path = os.path.join(input_dir, f'{example}.json')
                else:
                    input_path = os.path.join(input_dir, f'{input_size}.json')

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
                    mean_time, _outputs = run_multiple_times(command, os.environ.copy(), 1)
                    output['time'] = mean_time
                    output['output'] = _outputs[-1]
                except:
                    output[f'time'] = "TIMEOUT"
                    output[f'output'] = "N/A"
                    kill_process_by_name('temp_program')

                print('-------------')
                print(output)
                command_args['input_path'] = input_path

                if not writer:
                    writer = csv.DictWriter(outfile, fieldnames=output.keys())
                    writer.writeheader()
                writer.writerow(output)

# rows.sort(key=lambda a: a['test'], reverse=False)
