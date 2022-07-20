import os
import sys
import argparse

"""
This script is used to generate multiple csvs for a condor design run. You can input different numbers
for the spread of each geometry and the number of geometries to generate into this file below.
"""
# get the current date
date = os.popen('%Y-%m-%d').read().strip()
parser = argparse.ArgumentParser(description='Generate a csv file for a condor design run.')
parser.add_argument('-outputDir', '--outputDir', type=str, default=date, help='The output directory.')

# variables
outputDir = parser.outputDir
xShiftList = [6.3, ]
xSpreadList = [1, ]
crossingAngleList = []
angSpreadList = [10, ]


if __name__ == '__main__':
    # make the output directory that these will all output to
    makeOutputDir(outputDir)
    #install required packages for the below programs; these are found in requirements.txt
    #if you decide to add more packages to these programs, execute the below and it will update the requirements file:
    #   -pip freeze > requirements.txt
    #tips for requirements files:
    #  https://pip.pypa.io/en/latest/reference/requirements-file-format/#requirements-file-format
    #  gets rid of requirement output: https://github.com/pypa/pip/issues/5900?msclkid=474dd7c0c72911ec8bf671f1ae3975f0
    execInstallRequirements = "pip install -r " + requirementsFile + " | { grep -v 'already satisfied' || :; }" 
    os.system(execInstallRequirements)
