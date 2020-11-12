"""
File: origin.py
Author: AleNriG
Email: agorokhov94@gmail.com
Github: https://github.com/alenrig
Description: program for conversation unique SIMS files into csv-files for
import into Origin.
Usage: simply start this program into the files of interest directory.
"""


import numpy as np
import os
import pandas as pd


def read_file(file_input_path):
    """Files reader

    :file_input_path: TODO
    :returns: TODO

    """
    with open(file_input_path, 'r') as file:
        full_file = []
        for line in file.read().splitlines():
            full_file.append(line)
    return full_file


def files_collector():
    """Takes all txt files into current directory and puts their names into
    list.
    :returns: TODO

    """
    files_list = [datafile for datafile in os.listdir('.') if
                  datafile.endswith('txt')]
    return files_list


def cut_datapoints(full_file):
    """Cut all needed info and points into list and numpy.array.
    Strings '*** DATA START ***' and '*** DATA END ***' are marks for
    beggining and ending of datapoints.
    '+3' and '-1' are for cutting off empty strings.

    :full_file: TODO
    :returns: TODO

    """
    start_line = full_file.index('*** DATA START ***') + 3
    end_line = full_file.index('*** DATA END ***') - 1

    bad_header = full_file[start_line]
    header = parse_ions(bad_header)

    bad_points = full_text[start_line + 1:end_line]
    datapoints = []
    for line in bad_points:
        datapoints.append(line)
    return header, datapoints


def parse_ions(header):
    """Parse the string with ion names into list.

    :header: TODO
    :returns: TODO

    """
    return [ion.replace(' ', '') for ion in filter(None, header.split('\t'))]


if __name__ == "__main__":
    files_list = files_collector()
    for datafile in files_list:
        full_text = read_file(datafile)
        header, datapoints = cut_datapoints(full_text)
        datapoints = np.array(datapoints)

        data = pd.DataFrame(datapoints)
        data.columns = header
        filename = datafile.split('.')[0]
        data.to_csv(filename + '.csv', index=False, sep=',')
