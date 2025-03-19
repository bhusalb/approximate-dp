import time
import argparse
import csv
import os
import subprocess
import json


def run_command(command, env):
    start_time = time.time()

    process = subprocess.run(
        command,
        env=env,
        stdout=subprocess.PIPE,
        preexec_fn=os.setsid,
        timeout=100000,
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

input_dir = os.path.join(root_dir, 'examples', 'dipc_inputs')

main_script = os.path.join(root_dir, 'src', 'main.py')
rows = []

template = '''python {main} -f {file_path} -e {eps} -d {delta} --input {input_path} -k 8'''
characterization_template = '''python {main} -f {file_path} -e {eps} -d {delta} --characterize'''

eps = 0.5
delta = 0

# folders = ['svt_laplace', 'svt_laplace_max', 'svt', 'svt_max', 'nonpriv_svt', 'nonpriv_svt_max', 'noisy_max', 'noisy_min']

folder = 'svt_laplace_max'

# folders = ['nonpriv_svt', 'nonpriv_svt_max', ]

# folders = ['svt', 'svt_max', ]

with open(f'{root_dir}/results/result_dipc_private_1.csv', 'a', newline='') as outfile:
    # writer = csv.DictWriter(outfile, rows[0].keys())
    writer = None

    for eps in [1, 2]:

        examples_dir = os.path.join(root_dir, 'examples', folder)
        examples = os.listdir(examples_dir)

        for example in examples:
            i = int(example.split('.')[0].split('_')[-1])
            input_path = os.path.join(input_dir, f'{i}.json')
            output = dict(folder=folder, input_size=i, eps=eps, delta=delta, test=example)
            file_path = os.path.join(examples_dir, example)

            command_args = dict(main=main_script, file_path=file_path, eps=eps, delta=delta)

            _, characterization = run_command(characterization_template.format(**command_args), os.environ.copy())
            characterization = json.loads(characterization)

            output = output | characterization
            command_args['input_path'] = input_path
            command = template.format(**command_args)
            print(command)
            try:
                mean_time, outputs = run_multiple_times(command, os.environ.copy(), 2)
                output[f'time'] = mean_time
                output[f'output'] = outputs[-1]
            except:
                output[f'time'] = "TIMEOUT"
                output[f'output'] = "N/A"

            print(f'---{example}  time {output["time"]} output {output["output"]}---')
            if not writer:
                writer = csv.DictWriter(outfile, fieldnames=output.keys())
                writer.writeheader()
            writer.writerow(output)

# rows.sort(key=lambda a: a['test'], reverse=False)
