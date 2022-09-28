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

def getRandomGeometryGrid(numGeometries, ranges, xStarts, crossStarts):
    # create the output dataframe
    cols = 'xShift,crossingAngle,negAngle,axialRotation,negRot,zShift'.split(',')
    outputDf = pd.DataFrame(columns=cols)
    # get geometry range from ranges
    xShiftRange = ranges['xShift']
    crossingAngleRange = ranges['crossingAngle']
    axialRotationRange = ranges['axialRotation']
    zShiftRange = ranges['zShift']
    # loop through the xShifts and crossingAngles
    for xStart, cross in zip(xStarts, crossStarts):
        # define the xEnds and crossingAngleEnds
        xEnd = xStart + xShiftRange
        crossEnd = cross + crossingAngleRange
        # negative crossingAngle flag for design
        if (cross < 0):
            negAngle = 'false'
        else:
            negAngle = 'true'
        # loop through the number of geometries to get for each region
        for i in range(0,numGeometries):
            # get a random xShift, crossingAngle, axialRotation, and zShift
            xShift = round(rand.uniform(xStart, xEnd), 2)
            crossingAngle = round(rand.uniform(cross, crossEnd), 2)
            axialRotation = round(rand.uniform(0, axialRotationRange), 2)
            zShift = round(rand.uniform(0, zShiftRange), 2)
            # add these to the output dataframe
            outputDf = pd.concat([outputDf, pd.DataFrame([[xShift, crossingAngle, negAngle, axialRotation, 'true', zShift]], columns=cols)])
    return outputDf

def getSetGeometryGrid(ranges, increments, xStarts, crossStarts):
    cols = 'xShift,crossingAngle,negAngle,axialRotation,negRot,zShift,interface,sequence'.split(',')
    # get geometry range from ranges
    xShiftRange = ranges['xShift']
    crossingAngleRange = ranges['crossingAngle']
    axialRotationRange = ranges['axialRotation']
    zShiftRange = ranges['zShift']
    # get geometry increments from increments
    xInc = increments['xShift']
    crossInc = increments['crossingAngle']
    axInc = increments['axialRotation']
    zInc = increments['zShift']
    # loop through the xShifts and crossingAngles
    tmpDf = pd.DataFrame()
    for xStart, cross in zip(xStarts, crossStarts):
        # define the geometry ends
        # adjust ends: need to be higher to get the final desired increment
        xEnd = xStart + xShiftRange + xInc
        crossEnd = cross + crossingAngleRange + crossInc 
        axialEnd = axialRotationRange + axInc 
        zEnd = zShiftRange + zInc
        # negative crossingAngle flag for design
        if (cross < 0):
            negAngle = 'true'
            interface = '000110011001100110000'
            if (xStart < 8):
                sequence = 'LLLAGLLAGLLGALLGALILI'
            else:
                sequence = 'LLLAALLAALLAALLAALILI'
        else:
            negAngle = 'false'
            interface = '000011011001101100000'
            sequence = 'LLLLAALAALLAALAALLILI'
        # loop through geometries to get all values in grid
        xShiftList = np.arange(xStart, xEnd, xInc)
        crossingAngleList = abs(np.arange(cross, crossEnd, crossInc))
        axialRotationList = np.arange(0, axialEnd, axInc)
        zShiftList = np.arange(0, zEnd, zInc)
        # loop through the lists to get all combinations
        for xShift in xShiftList:
            x = round(xShift, 2)
            for crossingAngle in crossingAngleList:
                for axialRotation in axialRotationList:
                    for zShift in zShiftList:
                        print(x, crossingAngle, axialRotation, zShift, interface, sequence)
                        tmpDf = pd.concat([tmpDf, pd.DataFrame([[x, crossingAngle, negAngle, axialRotation, 'true', zShift, interface, sequence]], columns=cols)])
    return tmpDf

# Method to read config file settings
# Helper file for reading the config file of interest for running the program
def read_config(configFile):
    config = configparser.ConfigParser()
    config.read(configFile)
    return config

# get the configuration file for the current
def getConfigFile(configDir):
    configFile = ''
    # Access the configuration file for this program (should only be one in the directory)
    programDir = os.path.realpath(configDir)
    fileList = os.listdir(programDir)
    for file in fileList:
        fileName, fileExt = os.path.splitext(file)
        if fileExt == '.config':
            configFile = programDir + '/' + file
    if configFile == '':
        sys.exit("No config file present in script directory!")
    return configFile

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