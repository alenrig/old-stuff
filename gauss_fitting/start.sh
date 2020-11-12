#!/bin/bash

python_interpreter=python3
program=delta_layer.py

delta_params=tests/test_delta_params
raw_data=tests/test_data
processed_data_prefix=tests/test_output

${python_interpreter} ${program} ${delta_params} ${raw_data} ${processed_data_prefix}

gnuplot -e "original='${raw_data}'; outputprefix='${processed_data_prefix}'" plot_script.gpi
