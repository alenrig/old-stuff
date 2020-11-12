import numpy
import scipy
from scipy.special import erf
import matplotlib.pyplot as plt


#%% read input data
xGrid = []
data = []
with open('original.txt', 'r') as file:
    for line in file.read().splitlines():
        x, y = map(float, line.split())
        xGrid.append(x)
        data.append(y)

xGrid = numpy.array(xGrid)
data = numpy.array(data)

# estimate integral
deltaX = numpy.diff(xGrid).mean()
fullIntegral = numpy.trapz(data) * deltaX

# offset grid
midXIndex = data.argmax()
midX = xGrid[midXIndex]
xGridCentered = xGrid - midX
minX = min(xGridCentered)
maxX = max(xGridCentered)


#%% get transform function
# read transformation function params
lambdaG = float(input())
lambdaD = float(input())
sigma = float(input())
K = float(input())

# calculate the rest of params
a = 1 / lambdaG
b = 1 / lambdaD
p = 1 / 2 / sigma ** 2

# set grid
phiGrid = scipy.linspace(minX, maxX, num=5000)
deltaPhi = numpy.diff(phiGrid).mean()

# transformation function (direct space)
ksi1Grid = (phiGrid + a / 2 / p) * numpy.sqrt(p)
ksi2Grid = (phiGrid - b / 2 / p) * numpy.sqrt(p)
transFunction = K * (1 - erf(ksi1Grid)) * numpy.exp(a * phiGrid + a ** 2 / 4 / p)
transFunction += (1 + erf(ksi2Grid)) * numpy.exp(-b * phiGrid + b ** 2 / 4 / p)
transFunction = transFunction / 2 / (K / a + 1 / b)


#%% automatic fit cycle
depths = scipy.linspace(-50, +50, num=50)
widths = scipy.linspace(5, 100, num=20)
minDifference = 1e300
optimalDepth, optimalWidth = 0, 0
optimalFitFunction = numpy.zeros(len(phiGrid))
optimalRestoredData = numpy.zeros(len(phiGrid))
dataInterpolated = numpy.interp(phiGrid, xGridCentered, data)
for depth, width in [(a, b) for a in depths for b in widths]:
    print(depth, width)
    height = fullIntegral / width / numpy.sqrt(numpy.pi)
    fitFunction = height * numpy.exp(-((phiGrid - depth) / width) ** 2)
    restoredData = numpy.convolve(transFunction, fitFunction, 'same') * deltaPhi
    difference = sum((dataInterpolated - restoredData) ** 2)
    if difference < minDifference:
        minDifference = difference
        optimalDepth, optimalWidth = depth, width
        optimalFitFunction = fitFunction
        optimalRestoredData = restoredData
        print(depth, width, 'are new optimal, diff =', difference)

print('suboptimal params are:', optimalDepth, optimalWidth)
plt.figure()    
plt.plot(xGridCentered, data)
plt.plot(phiGrid, optimalFitFunction)
plt.plot(phiGrid, optimalRestoredData)
plt.xlabel('offset [nm]')
plt.ylabel('atomic concentration [cm^{-3}]')
plt.legend(['Original Signal', 'Fit distribution', 'Calculated Signal'])
plt.savefig('fitting.pdf')
plt.show()

with open('fit.txt', 'w') as file:
    for x, y in zip(phiGrid + midX, optimalFitFunction):
        file.write(str(x) + ' ' + str(y) + '\n')


##%% interactive fitting
#while True:
#    reply = input()
#    if reply == 'ok':
#        break
#    depth, width = map(float, reply.split()) # nm
#    height = fullIntegral / width / numpy.sqrt(numpy.pi)
#    fitFunction = height * numpy.exp(-((phiGrid - depth) / width) ** 2)
#
#    # dirty fit
#    restoredData = numpy.convolve(transFunction, fitFunction, 'same') * deltaPhi
#    plt.figure()
#    plt.plot(xGridCentered, data)
#    plt.plot(phiGrid, fitFunction)
#    plt.plot(phiGrid, restoredData)
#    plt.xlabel('offset [nm]')
#    plt.ylabel('atomic concentration [cm^{-3}]')
#    plt.legend(['Original Signal', 'Fit distribution', 'Calculated Signal'])
#    plt.show()
