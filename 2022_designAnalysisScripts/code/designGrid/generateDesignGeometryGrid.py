import sys
import os
import pandas as pd
import random as rand
import numpy as np
import configparser

"""
This script generates a csv file with all possible combinations of design parameters
for a given set of ranges.
"""

# read in the config file
configFile = sys.argv[1]

# Read in configuration file:
globalConfig = read_config(configFile)
config = globalConfig["main"]

# Config file options:
# read in the xShift, crossingAngle, axialRotation, and zShift ranges
xShiftRange = int(config["xShiftRange"])
crossingAngleRange = int(config["crossingAngleRange"])
axialRotationRange = int(config["axialRotationRange"])
zShiftRange = int(config["zShiftRange"])

# read in the xShift, crossingAngle, axialRotation, and zShift values to increment by
xInc = float(config["xIncrement"])
crossInc = float(config["crossIncrement"])
axInc = float(config["axIncrement"])
zInc = float(config["zIncrement"])

# read in number of geometries for random design grid
numGeometries = int(config["numGeometries"])

# read in the xShift and crossingAngle start values
GASrightXStart = float(config["GASrightXStart"])
GASrightCrossStart = float(config["GASrightCrossStart"])
rightXStart = float(config["rightXStart"])
rightCrossStart = float(config["rightCrossStart"])
leftXStart = float(config["leftXStart"])
leftCrossStart = float(config["leftCrossStart"])    

# get the current working directory
cwd = os.getcwd()

# set the output file name
outputFile = cwd + '/designGeometryGrid_test.csv'

# save ranges to a dictionary
ranges = {'xShift': xShiftRange, 'crossingAngle': crossingAngleRange, 'axialRotation': axialRotationRange, 'zShift': zShiftRange}
# get a list of xStarts and crossStarts
xStarts = [GASrightXStart, rightXStart, leftXStart]
crossStarts = [GASrightCrossStart, rightCrossStart, leftCrossStart]
# get random geometry grid values for each region
#df = getRandomGeometryGrid(numGeometries, ranges, xStarts, crossStarts)
#
## print outputDf to a csv file in the same directory as the original data file with no first column
#df.to_csv(outputFile, index=False)

# save increments to a dictionary
increments = {'xShift': xInc, 'crossingAngle': crossInc, 'axialRotation': axInc, 'zShift': zInc}
incrementDf = getSetGeometryGrid(ranges, increments, xStarts, crossStarts)
incrementDf.to_csv(cwd + '/incrementedDesignGeometryGrid_test.csv', index=False)