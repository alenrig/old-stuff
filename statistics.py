#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
File: statistics.py
Author: AleNriG
Email: agorokhov94@gmail.com
Github: https://github.com/alenrig
Description: Script for importing in IPython or similar for statistic and
quality calculations. Calculate mean, std and spline for every ion in data.

In this program are lots of using words like 'datafile', 'sample',
'filename', etc. To set things clear: we have file with standart form name,
for example: ZLN062_2-3_pos.csv. In this file:
    '_pos.csv' - no need in it;
    '2-3' - sample ID;
    'ZLN062' - number of measurement.
So in the program most of the time "filename" == "ZLN062_2-3"
or similar (depence on file of course), and "sample" == ""2-3"".

By now program calculate concentration profile for measurement, it dose;
calculate mean of concentration profile in each point, mean dose
and std of dose. Plot all measures and mean. Plot splined grapth.

Copyright © 2018 AleNriG. All Rights Reserved.
"""
import csv
import math
import os
import re
from itertools import dropwhile

import numpy as np
import pandas as pd
import scipy.interpolate as interpolate
from matplotlib import pyplot as plt
from scipy import signal


def _csv_grubber():
    """Grub all files in csv format in current directory.

    :returns: list of files.csv

    """
    return [datafile for datafile in os.listdir(".") if datafile.endswith("csv")]


def _read_file(input_file):
    """Read file.csv.
    WARNING! For correct work file.csv must be get from ascii files from
    CAMECA IMS 7f and converted into csv with converter.py.

    :input_file: file.csv
    :returns: dict('filename': filename, time': [...], 'ion 1': [...], etc)

    """
    data = dict(filename=input_file.rsplit("_", 1)[0])
    with open(input_file, "r") as file:
        legend, points = [], []
        for line in csv.reader(file):
            points.append(line)
    legend = points.pop(0)
    points = np.array(points)
    for number, label in enumerate(legend):
        data[label] = np.array(list(map(float, points[:, number])))
    return data


def _ions_set():
    """Create a set of all unique ions in datafiles in current directory.
    :returns: set of ions

    """
    datafiles = _csv_grubber()
    ions = []
    for datafile in datafiles:
        data = _read_file(datafile)
        for key in data:
            if not key.isalpha():
                ions.append(key)
    return set(ions)


def _strip_ion_name(ion):
    return "".join(dropwhile(lambda s: s.isdigit(), ion))


def _samples():
    """Create dict with sample ID as a key.
    Function read current directory and add to each key a list of measurements
    of this sample.

    :returns: dict(sample1: [filename1, filename2, etc], sample2: [...], etc)

    """
    samples = {}
    unique_samples = set(
        datafile.split("_", 1)[1].rsplit("_", 1)[0] for datafile in _csv_grubber()
    )
    for sample in unique_samples:
        samples[sample] = [
            datafile for datafile in _csv_grubber() if sample in datafile
        ]
    return samples


def _human_sort(x):
    """Sort ions in human acceptable form.
    Example:
        before _human_sort: sorted(ions list) == [115In, 11B];
        after _human_sort: sorted(ions list) == [11B, 115In].

    :x: don`t know.
    :returns: don`t know. Magic?

    """
    pattern = re.compile(r"(\d+)")
    element = pattern.split(x)
    return [int(y) if y.isdigit() else y for y in element]


def _integral(func, dx=1):
    """Calculate area under the function.
    dx - step for trapz.

    :data: dict('filename': filename, 'time': [...], etc)
    :returns: dict{'ion 1': area, etc}

    """
    return np.trapz(func, dx=dx)


def _choice(lst):
    """Choose one element from a list.

    :lst: list of something.
    :returns: chosen element.

    """
    for num, name in enumerate(lst, 1):
        print(f"{num:2d}. {name}")
    choice = int(input("Choice: ")) - 1
    if choice < 0 or choice >= len(lst):
        print("No such element, try again:")
        _choice(lst)
    return lst[choice]


def set_parameters():
    """Set constant parameters for all measures.

    :returns: dict('speed': ..., 'RSF': ..., etc)

    """
    parameters = dict(graphs_output_format=".pdf")
    parameters["data_output_format"] = ".txt"

    # Gathering ions from datafiles.
    ions = sorted(list(_ions_set()), key=_human_sort)
    print("Choose matrix: ")
    parameters["matrix"] = _choice(ions)
    # delete matrix from ions
    ions.remove(parameters["matrix"])

    for ion in ions:
        # IA -- Isotopic Abundance
        parameters[ion + " IA"] = float(input(ion + " IA: "))
        while 1 < parameters[ion + " IA"] or parameters[ion + " IA"] <= 0:
            print("Isotopic Abundance can be only in range from 0 to 1")
            parameters[ion + " IA"] = float(input(ion + " IA: "))
        parameters[ion + " RSF"] = float(input(ion + " RSF: "))
    return ions, parameters


def _area_calculator(datafile):
    """Calculate area under the ion/matrix function for each file in current
    directory.

    :datafile: inputed file (example: 'ZLN062_2-3')
    :returns: dict('ion 1': area, etc).

    """
    areas = {}
    data = _read_file(datafile)
    dx = np.diff(data["time"]).mean()
    for ion in ions:
        if ion in data:
            func = np.array(
                [i / m for i, m in zip(data[ion], data[parameters["matrix"]])]
            )
            areas[ion] = _integral(func[bad_points:], dx=dx)
    return areas


def compare_ions_intencity():
    """Print areas under the functions of ion/matrix for all datafiles in
    current directory.

    """
    for sample, datafiles in _samples().items():
        print(f"{sample:*^30}")
        datafiles = sorted(datafiles)
        for datafile in datafiles:
            print(f'{datafile.split("_")[0]:-^15}')
            for ion, area in _area_calculator(datafile).items():
                print(f"{ion} area = {area:.3g}")
        print(border)


def _concentration_calculator(data, ion):
    return np.array(
        [
            i / parameters[ion + " IA"] / m * parameters[ion + " RSF"]
            for i, m in zip(data[ion], data[parameters["matrix"]])
        ]
    )


def _concentration(data):
    """Calculate atomic concentration profile.
    Add a ['depth'] and ['concentration'] keys with values in data.

    :data: dict('filename': filename, 'time': [...], etc)

    """
    speed = float(input("Speed for " + data["filename"] + ": "))
    data["depth"] = data["time"] * speed
    dx = np.diff(data["depth"]).mean()

    for ion in ions:
        if ion in data:
            ion_name = _strip_ion_name(ion)
            data[ion_name] = _concentration_calculator(data, ion)
            data[ion_name + " dose"] = _integral(data[ion_name][bad_points:], dx=dx)


def _reper_point(data):
    """Calculate Reper point of ions.

    :data: dict('filename': ..., 'time': [...], 'depth': [...],
    'ion 1': [...], etc, 'concentration 1': [...], etc)

    """
    for ion_name in ion_names:
        if ion_name in data:
            data[ion_name + " Rp"] = np.sum(
                [
                    x * C / data[ion_name + " dose"]
                    for x, C in zip(data["depth"], data[ion_name])
                ]
            )
            data[ion_name + " ΔRp"] = math.sqrt(
                np.sum(
                    [
                        (x - data[ion_name + " Rp"]) ** 2 * C / data[ion_name + " dose"]
                        for x, C in zip(data["depth"], data[ion_name])
                    ]
                )
            )


def measure(datafile=None):
    """Return a measured chosen datafile with calculated concentration.

    :returns: dict('filename': filename, 'time': [...], 'depth': [...],
    'ion 1': [...], etc, 'concentration 1': [...], etc)

    """
    if datafile is None:
        files_list = sorted(_csv_grubber())
        print("Choose file:")
        data = _read_file(_choice(files_list))
    else:
        data = _read_file(datafile)

    _concentration(data)
    _reper_point(data)

    print(border)
    print(f'{data["filename"]:-^15}')
    for ion_name in ion_names:
        if ion_name in data:
            print(f"{ion_name} Rp = {data[ion_name + ' Rp']:.3e}")
            print(f"{ion_name} ΔRp = {data[ion_name + ' ΔRp']:.3e}")
            print(f"{ion_name} dose = {data[ion_name + ' dose']:.3e}")
    print(border)
    return data


def _means_calculator(means, *datas):
    """Create a list of lists of measurements for each ion from every input data.
    Calculate mean of measurements point by point. Calculate mean of doses and
    doses std.

    :means: dict("sample": sample)
    :*datas: all inputed datas to calculate mean from them.

    """
    means["depth"] = []
    for ion_name in ion_names:
        means[ion_name] = []
        means[ion_name + " dose"] = []
        means[ion_name + " dose std"] = []

    for data in datas:
        means["depth"].append(data["depth"])
        for key, value in data.items():
            if key in ion_names:
                means[key].append(value)
                means[key + " dose"].append(data[key + " dose"])

    means["depth"] = np.array([np.mean(i) for i in zip(*means["depth"])])
    for key, values in means.items():
        if key in ion_names:
            means[key] = np.array([np.mean(i) for i in zip(*values)])
            means[key + " dose std"] = np.std(means[key + " dose"])
            means[key + " dose"] = np.mean(means[key + " dose"])


def mean(*datas, sample=None):
    """Calculate means for all inputted data of given sample.
    If sample is not given - read firs filename and take it from there.

    :*datas: data1, data2, etc
    :sample: sample ID
    :returns: dict('depth': [...], 'ion1 mean': [...], ...,
    'ion 1 std': [...], etc)

    """

    # if function running from interpretor.
    if sample is None:
        filenames = [data["filename"] for data in datas]
        sample = filenames[0].rsplit("_")[0]

    means = dict(sample=sample)
    _means_calculator(means, *datas)

    print(f"{sample:*^30}")
    for ion_name in ion_names:
        if ion_name in means:
            print(f"{ion_name} mean dose = {means[ion_name + ' dose']:.3e}")
            print(f"{ion_name} dose std = {means[ion_name + ' dose std']:.3e}")
    print(border)

    return means


def write_file(dict_of_data):
    """Save inputed dictionary to file.txt.
    Function use pandas to correct saving of dictionary. It is necessary to
    remove some values fro a dataframe (example: 'sample').

    :dict_of_data: dict from measure() or from mean()

    """
    dataframe = pd.DataFrame.from_dict(dict_of_data)
    if "filename" in dict_of_data:
        del dataframe["filename"]
        for ion_name in ion_names:
            if ion_name in dict_of_data:
                # remove excessive data
                del dataframe[ion_name + " dose"], dataframe[ion_name + " Rp"]
                del dataframe[ion_name + " ΔRp"]
        dataframe.to_csv(
            dict_of_data["filename"] + parameters["data_output_format"],
            index=False,
            sep=",",
        )
    elif "sample" in dict_of_data:
        del dataframe["sample"]
        for ion_name in ion_names:
            if ion_name in dict_of_data:
                # remove excessive data
                del dataframe[ion_name + " dose"]
                del dataframe[ion_name + " dose std"]
        dataframe.to_csv(
            dict_of_data["sample"] + parameters["data_output_format"],
            index=False,
            sep=",",
        )
    else:
        print("fuck")


def plot(dict_of_data):
    """Plot inputted dictionary. If dict_of_data is mean -- plot splined as well.
    Save grapths as file.pdf.

    :dict_of_data: dict from measure() or from mean()

    """

    # if dict_of_data is one measure.
    if "filename" in dict_of_data:
        plt.figure()
        plt.title(dict_of_data["filename"])
        for ion_name in ion_names:
            if ion_name in dict_of_data:
                plt.plot(dict_of_data["depth"], dict_of_data[ion_name], label=ion_name)
        plt.yscale("log")
        plt.ylabel("Atomic concentration, cm$^{-3}$")
        plt.xlim(left=0)
        plt.xlabel("Depth, nm")
        plt.grid(True)
        plt.legend()
        plt.show(block=False)
        plt.savefig(dict_of_data["filename"] + parameters["graphs_output_format"])

    # if dict_of_data is mean of several measures.
    elif "sample" in dict_of_data:
        plt.figure()
        plt.title(dict_of_data["sample"] + " Mean")
        for ion_name in ion_names:
            if ion_name in dict_of_data:
                peaks, _ = signal.find_peaks(dict_of_data[ion_name], height=1e17)
                plt.plot(dict_of_data["depth"], dict_of_data[ion_name], label=ion_name)
                plt.plot(
                    dict_of_data["depth"][peaks], dict_of_data[ion_name][peaks], "x"
                )

        plt.yscale("log")
        plt.ylabel("Atomic concentration, cm$^{-3}$")
        plt.xlim(left=0)
        plt.xlabel("Depth, nm")
        plt.grid(True)
        plt.legend()
        plt.show(block=False)
        plt.savefig(dict_of_data["sample"] + parameters["graphs_output_format"])

        # Spline plot.
        dict_of_data["depth splined"] = np.linspace(
            dict_of_data["depth"][0], dict_of_data["depth"][-1], spline_dots
        )

        plt.figure()
        plt.title(dict_of_data["sample"] + " Spline")
        for ion_name in ion_names:
            if ion_name in dict_of_data:
                # BSpline magic
                t, c, k = interpolate.splrep(
                    dict_of_data["depth"], dict_of_data[ion_name], s=0, k=4
                )
                spline = interpolate.BSpline(t, c, k, extrapolate=False)
                plt.plot(
                    dict_of_data["depth splined"],
                    spline(dict_of_data["depth splined"]),
                    label=ion_name,
                )
        plt.yscale("log")
        plt.ylabel("Atomic concentration, cm$^{-3}$")
        plt.xlim(left=0)
        plt.xlabel("Depth, nm")
        plt.grid(True)
        plt.legend()
        plt.show(block=False)
        plt.savefig(
            dict_of_data["sample"] + "_splined" + parameters["graphs_output_format"]
        )

    else:
        print("fuck")


def main():
    """Automatic calculations for sample.

    """
    while True:
        print("Choose sample: ")
        sample = _choice(sorted(list(_samples().keys()), key=_human_sort))
        datas = []
        for datafile in sorted(_samples()[sample], key=_human_sort):
            data = measure(datafile=datafile)
            plot(data)
            write_file(data)
            datas.append(data)
        means = mean(*datas, sample=sample)
        write_file(means)
        plot(means)
        answer = input("quit? [q]: ")
        if answer == "q":
            break


# Initialize values on loading the module
bad_points = int(input("Bad points: "))  # first points in data is bad
ions, parameters = set_parameters()
ion_names = list(map(_strip_ion_name, ions))
spline_dots = int(input("Dots for spline: "))
border = "*" * 30


if __name__ == "__main__":
    main()
