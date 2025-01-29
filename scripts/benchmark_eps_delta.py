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


parser = argparse.ArgumentParser(description='Benchmarking tool')
# parser.add_argument('--folder', '-f', type=str, required=True)
parser.add_argument('--input', '-i', action='store_true', required=False, default=False)

args = parser.parse_args()

root_dir = os.path.join(os.path.dirname(__file__), '../')

input_dir = os.path.join(root_dir, 'examples', 'inputs')

main_script = os.path.join(root_dir, 'src', 'main.py')
rows = []

benchmark_time_template = '''python {main} -f {file_path} -e {eps} -d {delta} --input {input_path}'''

characterization_template = '''python {main} -f {file_path} -e {eps} -d {delta} --characterize'''

# folders = ['svt', 'svt_max', 'noisy_max', 'noisy_min']
folders = ['svt', ]

type_to_title = {
    'svt': r'\AboveThreshold',
    'svt_max': r'\BelowThreshold',
    'noisy_min': r'\NoisyMin',
    'noisy_max': r'\NoisyMax',

}
outfile = open(f'{root_dir}/results/result_new_scaling.csv', 'w', newline='')

writer = None

for folder in folders:
    examples_dir = os.path.join(root_dir, 'examples', folder)
    # examples = os.listdir(examples_dir)
    examples = ['example_5.dip']
    for eps in [0.05, 0.08, 0.09, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]:
        for delta in [0.01, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6]:
            for example in examples:
                i = int(example.split('.')[0].split('_')[-1])
                input_path = os.path.join(input_dir, f'inputs_{i}.json')
                output = dict(eps=eps, delta=delta, type=type_to_title[folder])
                output['test'] = example
                file_path = os.path.join(examples_dir, example)

                command_args = dict(main=main_script, file_path=file_path, eps=eps, delta=delta)

                _, characterization = run_command(characterization_template.format(**command_args), os.environ.copy())
                characterization = json.loads(characterization)

                output = output | characterization

                command_args['input_path'] = input_path

                command = benchmark_time_template.format(**command_args)

                print(command)
                try:
                    mean_time, outputs = run_multiple_times(command, os.environ.copy(), 3)
                    output['time'] = mean_time
                    output['output'] = outputs[-1]
                except:
                    output['time'] = "TIMEOUT"
                    output['output'] = "N/A"
                    print(f"TIMEOUT")
                print('----------------------------------------------------------')

                if not writer:
                    writer = csv.DictWriter(outfile, output.keys())
                    writer.writeheader()
                writer.writerow(output)
                rows.append(output)

    # rows.sort(key=lambda a: a['test'], reverse=False)

outfile.close()
