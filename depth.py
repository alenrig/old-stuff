"""Пересчёт скорости травления образца, в зависимости от состава матрицы.
Необходимо знать индексы точек перехода от одного слоя к другому.
Необходимо знать скорости травления в каждом слое.

Использование: python3 prog.py file.

"""
import csv
import sys

import numpy as np


def prog_usage():
    """Печать инструкции использования."""
    print("Использование: python3", sys.argv[0], "файл данных.")


def file_read(file_input_path):
    data = {}
    with open(file_input_path) as file:
        points, legend = [], []
        for line in csv.reader(file):
            points.append(line)
        legend = points.pop(0)
        points = np.array(points)
        for number, element in enumerate(legend):
            data[element] = [float(i) for i in points[:, number]]
    return data


class DepthCalculator:
    """Класс расчета списка глубины для гомо- и гетероструктур."""

    control = []

    def __init__(self, init=1):
        self.layers = init

    def _speed_and_control(self):
        """Ввод и проверка значения скорости."""
        speed = float(input("Введите скорость травления слоя: "))
        while speed <= 0:
            print("Скорость травления не может быть отрицательна.")
            speed = float(input("""Введите скорость травления слоя: """))
        return speed

    def _index_and_control(self):
        """Ввод и проверка значения индекса."""
        for layer in range(self.layers - 1):
            index = int(input("Введите индекс точки смены слоя: "))
            while index <= 0 or index in self.control:
                print(
                    "Индекс должен быть положительным числом. \
                      Значения индексов не могут повторяться. \
                      Повторите ввод."
                )
                index = int(input("Введите индекс точки смены слоя: "))
            self.control.append(index)
        return self.control

    def depth(self, grid):
        list_of_indexes = self._index_and_control()
        if list_of_indexes == []:
            speed = self._speed_and_control()
            depth = [grid[i] * speed for i in range(len(grid))]
        else:
            for layer in range(self.layers):
                if layer == 0:
                    speed = self._speed_and_control()
                    index = list_of_indexes[layer]
                    depth = [grid[i] for i in range(len(grid[:index]))]
                elif layer == self.layers - 1:
                    speed = self._speed_and_control()
                    index = list_of_indexes[layer - 1]
                    grid_end = grid[index:]
                    depth_end = [grid_end[i] * speed for i in range(len(grid_end))]
                    depth += depth_end
                else:
                    speed = self._speed_and_control()
                    index_left = list_of_indexes[layer - 1]
                    index_right = list_of_indexes[layer]
                    grid_middle = grid[index_left:index_right]
                    depth_middle = [
                        grid_middle[i] * speed for i in range(len(grid_middle))
                    ]
                    depth += depth_middle
        return depth


if __name__ == "__main__":

    data = file_read(sys.argv[1])

    layers = int(input("Введите количество слоев: "))
    while layers <= 0:
        print("Количество слоев не может быть меньше либо равно нулю.")
        layers = int(input("Введите количество слоев: "))

    dc = DepthCalculator(layers)
    data["depth"] = dc.depth(data["time"])
