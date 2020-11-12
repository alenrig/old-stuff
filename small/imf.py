# Расчёт 

while True:

    c1 = float(input('Insert major C: '))
    c2 = float(input('Insert minor C: '))
    p1 = float(input('Insert major %: '))
    p2 = float(input('Insert minor %: '))

    IMF = c2 * p1 / c1 / p2
    print('IMF =', IMF)

    print('Again? [y/n]: ')
    y = input()
    if y != 'y':
        break
