import os
import sys
import argparse
from datetime import date
from functions import *

"""
This script is used to generate multiple csvs for a condor design run. You can input different numbers
for the spread of each geometry and the number of geometries to generate into this file below.
"""
# get the current date
path = os.getcwd()
today = str(date.today())
outDir = path + '/' + today

# parse through options
parser = argparse.ArgumentParser(description='Generate a csv file for a condor design run.')
parser.add_argument('-outputDir', '--outputDir', type=str, default=outDir, help='The output directory.')
args = parser.parse_args()

# variables
outputDir = args.outputDir
xShiftList = [6.3, 8, 8.75]
xSpreadList = [1.2, 1, 1]
crossingAngleList = [-50, -50, 25]
angSpreadList = [15, 15, 15]
filenames = ['gxxxg', 'right', 'left']

if __name__ == '__main__':
    # make the output directory that these will all output to
    makeOutputDir(outputDir)
    #install required packages for the below programs; these are found in requirements.txt
    #if you decide to add more packages to these programs, execute the below and it will update the requirements file:
    #   -pip freeze > requirements.txt
    #tips for requirements files:
    #  https://pip.pypa.io/en/latest/reference/requirements-file-format/#requirements-file-format
    #  gets rid of requirement output: https://github.com/pypa/pip/issues/5900?msclkid=474dd7c0c72911ec8bf671f1ae3975f0
    requirementsFile = path+'/'+'requirements.txt'
    execInstallRequirements = "pip install -r " + requirementsFile + " | { grep -v 'already satisfied' || :; }" 
    os.system(execInstallRequirements)

    # execute generateGeomCsv script 
    for xShift, xSpread, crossingAngle, angSpread, filename in zip(xShiftList, xSpreadList, crossingAngleList, angSpreadList, filenames):
        execScript = 'python generateGeomCsv.py -outputDir ' + outputDir + ' -xShift ' + str(xShift) + ' -xSpread ' + \
         str(xSpread) + ' -crossingAngle ' + str(crossingAngle) + ' -angSpread ' + str(angSpread) + ' -filename ' + filename
        os.system(execScript)