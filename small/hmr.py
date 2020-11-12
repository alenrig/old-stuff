# Расчёт High Mass Resolution

while True:
    mass1 = eval(input('Input the 1st mass: '))
    mass2 = eval(input('Input the 2nd mass: '))
    HMR = mass2 / abs(mass1 - mass2)
    print('The value of HMR is:', int(HMR))

    print('Again? [y/n]: ')
    y = str(input())
    if y != 'y':
        break
