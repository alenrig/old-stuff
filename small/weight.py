#Вычисление весового коэффициент K_a для твёрдого раствора вида A_xB_(1-x)C.

while True:
    print('For your structure A_xB_(1-x)C, input theese data:')
    # А, В - средние значения интенсивности.
    a = float(input('Input mean of A: '))
    b = float(input('Input mean of B: '))

    # NA - natural abundance - изотопная распространённость веществ А и В.
    print('NA - natural abundance')
    la = float(input('Input NA of A (in %): '))
    lb = float(input('Input NA of B (in %): '))

    # x - концентрация эл-та А.
    x = float(input('Input x - concentration (from 0 to 1): '))
    k = x * b * la / 100 / lb / 100 / a / (1 - x)
    print("Weight function for A:", k) 
    
    answer = input("Again? [y/n]: ")
    if answer != 'y':
        break
