import time
import argparse
import csv
import os
import subprocess
import json
import signal
import psutil


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
        timeout=600,
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

root_dir = os.path.join(os.path.dirname(__file__), '../')

input_dir = os.path.join(root_dir, 'examples', 'inputs')

main_script = os.path.join(root_dir, 'src', 'main.py')
rows = []

benchmark_time_template_single_inputs = '''python {main} -f {file_path} -e {eps} -d {delta} --input {input_path} -k {k} --epriv {epriv}'''
benchmark_time_template_all_inputs = '''python {main} -f {file_path} -e {eps} -d {delta} -k {k} --epriv {epriv}'''
characterization_template = '''python {main} -f {file_path} -e {eps} -d {delta} --characterize -k {k} --epriv {epriv}'''

eps = 0.5
delta = 0.01
epriv = 1.24

folders = [
    # 'svt_laplace',
    # 'svt_laplace_max',
    'svt',
    'svt_max',
    # 'svt_mix1',
    # 'svt_mix2',
    # 'svt_mix1_max',
    # 'svt_mix2_max',
    # 'nonpriv_svt',
    # 'nonpriv_svt_max',
    # 'noisy_max',
    # 'noisy_min',
    # 'mrange',
    # 'kminmax',
    # 'noisy_max_laplace',
    # 'noisy_min_laplace',
    # 'new_nonpriv_svt',
    # 'new_nonpriv_svt_max'
]

# folders = ['svt_laplace', 'svt_laplace_max', ]

# folders = ['nonpriv_svt', 'nonpriv_svt_max', ]

# folders = ['svt', 'svt_max', ]

with open(f'{root_dir}/results/new_all_data.csv', 'a', newline='') as outfile:
    # writer = csv.DictWriter(outfile, rows[0].keys())
    writer = None

    for folder in folders:
        examples_dir = os.path.join(root_dir, 'examples', folder)
        examples = os.listdir(examples_dir)

        for example in examples:
            i = int(example.split('.')[0].split('_')[-1])

            input_path = os.path.join(input_dir, f'inputs_{i}.json')
            output = dict(folder=folder, input_size=i, eps=eps, delta=delta, test=example)
            file_path = os.path.join(examples_dir, example)

            command_args = dict(main=main_script, file_path=file_path, eps=eps, delta=delta, k=4, epriv=eps)

            if folder in ['svt', 'svt_max', 'svt_mix1', 'svt_mix2', 'svt_mix1_max', 'svt_mix2_max']:
                command_args['epriv'] = epriv

            if 'laplace' in folder or 'mix' in folder:
                command_args['k'] = 8

            _, characterization = run_command(characterization_template.format(**command_args), os.environ.copy())
            characterization = json.loads(characterization)

            output = output | characterization
            all_templates = dict(all=benchmark_time_template_all_inputs, single=benchmark_time_template_single_inputs)
            for _type, template in all_templates.items():
                command = template.format(**command_args)
                print(command)

                if i >= 8 and _type == 'all':
                    output[f'time_{_type}'] = "TIMEOUT"
                    output[f'output_{_type}'] = "N/A"
                else:
                    try:
                        mean_time, outputs = run_multiple_times(command, os.environ.copy(), 3)
                        output[f'time_{_type}'] = mean_time
                        output[f'output_{_type}'] = outputs[-1]
                    except:
                        output[f'time_{_type}'] = "TIMEOUT"
                        output[f'output_{_type}'] = "N/A"
                        kill_process_by_name('temp_program')
                command_args['input_path'] = input_path
            print(output)
            if not writer:
                writer = csv.DictWriter(outfile, fieldnames=output.keys())
                # writer.writeheader()
            writer.writerow(output)

# rows.sort(key=lambda a: a['test'], reverse=False)
