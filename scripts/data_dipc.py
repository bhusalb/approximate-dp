import os, csv


def read_csv(filename):
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        data = dict()
        for row in reader:
            folder = row['folder']
            test = row['test']
            data[f'{folder}_{test}'] = row
        return data
