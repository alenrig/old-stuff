#!/bin/bash

chose(){
echo "From this programs:"
ls *.py; echo
echo "Enter the name of one you need (without .py):" 
read prog; echo
}

chose
if [[ ! -f ${prog}.py ]]
then
    echo "Error! There is no such program, try again."
    chose
fi
head -n 1 ${prog}.py

# run program
python_interpreter=ipython3
${python_interpreter} ${prog}.py
