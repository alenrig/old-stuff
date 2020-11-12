''' Восстановление распределения дельта-слоя без влияния перемешанного слоя '''
import csv
import sys

import matplotlib.pyplot as plt
import numpy
import scipy
from scipy.special import erf


def read_data(file_path):
    grid, data = [], []
    with open(file_path) as file:
        for line in csv.reader(file):
            x, y = map(float, line)
            grid.append(x)
            data.append(y)
    return numpy.array(grid), numpy.array(data)


def write_data(file_path, phi_grid, optimal_fitfunction):
    with open(file_path, 'w') as file:
        for x, y in zip(phi_grid, optimal_fitfunction):
            file.write('{} {:e}\n'.format(x, y))


def calculate_transfunction(lambda_g, lambda_d, sigma, K):
    '''Расчет ответной функции по коэффициентам'''
    a = 1 / lambda_g
    b = 1 / lambda_d
    p = 1 / 2 / sigma ** 2

    ksi1_grid = (phi_grid + a / 2 / p) * numpy.sqrt(p)
    ksi2_grid = (phi_grid - b / 2 / p) * numpy.sqrt(p)
    transfunction = K * (1 - erf(ksi1_grid)) * numpy.exp(a * phi_grid + a ** 2 / 4 / p)
    transfunction += (1 + erf(ksi2_grid)) * numpy.exp(-b * phi_grid + b ** 2 / 4 / p)
    transfunction = transfunction / 2 / (K / a + 1 / b)
    return transfunction


if __name__ == '__main__':
    # проверка аргументов командной строки
    if len(sys.argv) == 3:
        input_path = sys.argv[1]
        output_path = sys.argv[2]
    else:
        print('usage: {} input_file output_file'.format(sys.argv[0]))
        exit(1)

    # чтение и нормирование данных
    xgrid, data = read_data(input_path)
    delta_x = numpy.diff(xgrid).mean()
    full_integral = numpy.trapz(data) * delta_x

    # центровка данных по точке экстремума
    midx_index = data.argmax()
    midx = xgrid[midx_index]
    xgrid_centered = xgrid - midx
    minx = min(xgrid_centered)
    maxx = max(xgrid_centered)

    # set grid
    phi_grid = scipy.linspace(minx, maxx, num=5000)
    delta_phi = numpy.diff(phi_grid).mean()

    # ответная функция
    lambda_g = float(input('Input lambda g: '))
    lambda_d = float(input('Input lambda d: '))
    sigma = float(input('Input sigma: '))
    K = float(input('Input K: '))
    transfunction = calculate_transfunction(lambda_g, lambda_d, sigma, K)

    # цикл подгона гауссовского распределения к экспериментальным данным
    depths = scipy.linspace(-50, +50, num=50)
    widths = scipy.linspace(5, 100, num=20)
    min_difference = 1e300
    optimal_depth, optimal_width = 0, 0
    optimal_fitfunction = numpy.zeros(len(phi_grid))
    optimal_restored_data = numpy.zeros(len(phi_grid))
    data_interpolated = numpy.interp(phi_grid, xgrid_centered, data)
    for depth, width in [(a, b) for a in depths for b in widths]:
        print(depth, width)
        height = full_integral / width / numpy.sqrt(numpy.pi)
        fitfunction = height * numpy.exp(-((phi_grid - depth) / width) ** 2)
        restored_data = delta_phi * numpy.convolve(transfunction,
                                                   fitfunction,
                                                   'same')
        difference = sum((data_interpolated - restored_data) ** 2)
        if difference < min_difference:
            min_difference = difference
            optimal_depth, optimal_width = depth, width
            optimal_fitfunction = fitfunction
            optimal_restored_data = restored_data
            print(depth, width, 'are new optimal, diff =', difference)

    print('suboptimal params are:', optimal_depth, optimal_width)
    write_data(output_path, phi_grid, optimal_fitfunction)

    # построение граффиков
    plt.figure()
    plt.plot(xgrid_centered, data)
    plt.plot(phi_grid, optimal_fitfunction)
    plt.plot(phi_grid, optimal_restored_data)
    plt.xlabel('depth [nm]')
    plt.ylabel('atomic concentration [cm^{-3}]')
    plt.legend(['Original Signal',
                'Restored distribution',
                'Calculated Experimental Signal'])
    plt.savefig('fitting.pdf')
    plt.show()
