import sys
import numpy
import scipy
from scipy.special import erf


# constants
MAX_POINTS_XGRID = 1000
MINDEPTH, MAXDEPTH, DEPTHSTEP =-20, 20, 0.5
MINWIDTH, MAXWIDTH, WIDTHSTEP = 1, 100, 1


def print_usage():
    print("usage: " + sys.argv[0] + " PARAMS_FILE INPUT_FILE OUTPUT_FILE")


def read_data(file_path):
    grid, data = [], []
    with open(file_path, 'r') as file:
        for line in file.read().splitlines():
            x, y = map(float, line.split())
            grid.append(x)
            data.append(y)
    return numpy.array(grid), numpy.array(data)


def write_data(file_path, xs, ys):
    with open(file_path, 'w') as file:
        for x, y in zip(xs, ys):
            file.write('{:e} {:e}\n'.format(x, y))


def center_grid(grid, data):
    mid_index = data.argmax()
    mid_x = grid[mid_index]
    return (grid - mid_x), mid_x


def read_impulse_params(file_path):
    with open(file_path, 'r') as file:
        params = file.read().splitlines()
        lambda_g, lambda_d, sigma, K = map(float, params)
        return lambda_g, lambda_d, sigma, K


class ImpulseFunctionCreator(object):
    def __init__(self, params):
        lambda_g, lambda_d, sigma, K = params
        self.K = K
        self.sigma = sigma
        self.a = 1 / lambda_g
        self.b = 1 / lambda_d
        self.p = 1 / 2 / sigma ** 2
        self.lambda_g = lambda_g
        self.lambda_d = lambda_d

    def create(self, grid):
        ksi1_grid = (grid + self.a / 2 / self.p) * numpy.sqrt(self.p)
        ksi2_grid = (grid - self.b / 2 / self.p) * numpy.sqrt(self.p)
        impulse_function = self.K * (1 - erf(ksi1_grid)) * numpy.exp(self.a * grid + self.a ** 2 / 4 / self.p)
        impulse_function += (1 + erf(ksi2_grid)) * numpy.exp(- self.b * grid + self.b ** 2 / 4 / self.p)
        impulse_function /= 2 * (self.K / self.a + 1 / self.b)
        return impulse_function


def full_search_fitting(response, impulse_function, grid, depths, widths):
    min_difference = 1e500
    optimal_depth, optimal_width = 0, 0
    optimal_input = numpy.zeros(len(grid))
    optimal_response = numpy.zeros(len(grid))
    integral_signal = numpy.trapz(y=response, x=grid)
    delta_grid = numpy.diff(grid).mean()
    for depth, width in [(d, w) for d in depths for w in widths]:
        print(depth, width)
        height = integral_signal / width / numpy.sqrt(numpy.pi)
        test_input = height * numpy.exp(-((grid - depth) / width) ** 2)
        test_response = numpy.convolve(impulse_function, test_input, 'same') * delta_grid
        difference = sum((response - test_response) ** 2)
        if difference < min_difference:
            min_difference = difference
            optimal_depth, optimal_width = depth, width
            optimal_input = test_input
            optimal_response = test_response
            print("    improvement:", difference)
    return optimal_depth, optimal_width, optimal_input, optimal_response


def main():
    # check the command line arguments
    if len(sys.argv) != 4:
        print("wrong number of arguments")
        print_usage()
        exit(1)

    # read the impulse function params
    params_path = sys.argv[1]
    params = read_impulse_params(params_path)
    impulse_function_creator = ImpulseFunctionCreator(params)

    # read the input file
    inputfile_path = sys.argv[2]
    grid, data = read_data(inputfile_path)
    centered_grid, mid_x = center_grid(grid, data)

    # automatic fitting
    fit_grid = scipy.linspace(min(centered_grid), max(centered_grid), num=MAX_POINTS_XGRID)
    data_interpolated = numpy.interp(fit_grid, centered_grid, data)
    impulse_function = impulse_function_creator.create(fit_grid)
    depths_range = numpy.arange(start=MINDEPTH, stop=MAXDEPTH, step=DEPTHSTEP)
    widths_range = numpy.arange(start=MINWIDTH, stop=MAXWIDTH, step=WIDTHSTEP)
    optimal_fit = full_search_fitting(data_interpolated, impulse_function, fit_grid, depths_range, widths_range)
    optimal_depth, optimal_width, optimal_input, optimal_response = optimal_fit
    print('optimal params are:', optimal_depth, optimal_width)

    # save files
    output_prefix = sys.argv[3]
    write_data(output_prefix + '_input', fit_grid + mid_x, optimal_input)
    write_data(output_prefix + '_response', fit_grid + mid_x, optimal_response)


if __name__ == "__main__":
    main()
