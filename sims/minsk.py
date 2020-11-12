"""
File: minsk.py
Author: AleNriG
Email: agorokhov94@gmail.com
Github: https://github.com/alenrig
Description: program for MINSK-Integral. Program collecting last points of
user choise and count mean for each file and mean of all means for sample.

Copyright © 2018 AleNriG. All Rights Reserved.
"""


import csv
import numpy as np
import os


def file_read(file_input_path):
    """Read files and turn them into dicts.

    :file_input_path: TODO
    :returns: TODO

    """
    data = {}
    with open(file_input_path, 'r') as file:
        points, legend = [], []
        for line in csv.reader(file):
            points.append(line)
    legend = points.pop(0)
    points = np.array(points)
    for number, element in enumerate(legend):
        data[element] = [float(i) for i in points[:, number]]
    return data


def file_write(result):
    """Write all results into file.

    :result: TODO

    """
    with open('result.txt', 'w') as file:
        for key, value in result.items():
            file.write(key)
            means = []
            for filename, mean in value.items():
                file.write(
                    '\nдля файла {} среднее - {:.3e}'.format(filename, mean))
                means.append(mean)
            file.write('\nсреднее {:.3e}'.format(np.mean(means)))
            file.write('\n---\n')


def combine_by_samples():
    """Group all files by samples their belong.

    :returns: TODO

    """
    combined = {}
    samples = set(datafile.split('_', 1)[1].rsplit('_', 1)[0]
                  for datafile in os.listdir('.') if datafile.endswith('.csv'))
    for sample in samples:
        combined[sample] = [datafile for datafile in os.listdir('.')
                            if datafile.endswith('.csv') and
                            sample in datafile]
    return combined


def mean_calc():
    """Calculate mean for every file.
    :returns: TODO

    """
    rsf = float(input('Введите RSF: '))
    points = int(input('Введите количество точек, по которым будет '
                       'проводится рассчет: '))

    combined = combine_by_samples()
    result = {}
    for key, value in combined.items():
        means = {}
        for datafile in value:
            data = file_read(datafile)
            filename = datafile.split('_')[0]
            RSF = [alloy / matrix / 0.8 * rsf
                   for alloy, matrix in zip(data['11B'], data['30Si'])]
            mean = np.mean(RSF[-points:])
            means.update({filename: mean})
        result[key] = means
    return result


if __name__ == '__main__':

    result = mean_calc()
    file_write(result)
