# Расчёт RSF с учётом единиц исчисления

while True:
    D = float(input('input D: '))
    integer = float(input('input the result of integer of I_n/I_M: '))
    RSF = D / integer * 10 ** 7
    print('RSF = %e' % RSF)

    answer = input('Again? [y/n]: ')
    if answer != 'y':
        break
