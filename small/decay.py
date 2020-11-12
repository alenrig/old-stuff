# Расчёт скорости спада.

from math import log

while True:
    x1 = float(input('Input x1: '))
    y1 = float(input('Input y1: ')) # y1, y2 - точки, на которых сигнал упал в е раз.
    x2 = float(input('Input x2: '))
    y2 = float(input('Input y2: '))
    l = -(x2 - x1) / log(y2 / y1)
    print("Decay length:", l)

    answer = input("Again? [y/n]: ")
    if answer != 'y':
        break
