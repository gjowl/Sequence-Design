import sys
import os
import pandas as pd
import random as rand
import numpy as np

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
    cols = 'xShift,crossingAngle,negAngle,axialRotation,negRot,zShift'.split(',')
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
        xEnd = xStart + xShiftRange + 0.5
        crossEnd = cross + crossingAngleRange + 0.5 
        axialEnd = axialRotationRange + 1
        zEnd = zShiftRange + 1
        # negative crossingAngle flag for design
        if (cross < 0):
            negAngle = 'true'
        else:
            negAngle = 'false'
        # loop through geometries to get all values in grid
        xShiftList = np.arange(xStart, xEnd, xInc)
        crossingAngleList = abs(np.arange(cross, crossEnd, crossInc))
        axialRotationList = np.arange(0, axialEnd, axInc)
        zShiftList = np.arange(0, zEnd, zInc)
        # loop through the lists to get all combinations
        for xShift in xShiftList:
            for crossingAngle in crossingAngleList:
                for axialRotation in axialRotationList:
                    for zShift in zShiftList:
                        tmpDf = pd.concat([tmpDf, pd.DataFrame([[xShift, crossingAngle, negAngle, axialRotation, 'true', zShift]], columns=cols)])
    return tmpDf

# read in the xShift, crossingAngle, axialRotation, and zShift ranges
xShiftRange = 1
crossingAngleRange = 10
axialRotationRange = 100
zShiftRange = 6

# save ranges to a dictionary
ranges = {'xShift': xShiftRange, 'crossingAngle': crossingAngleRange, 'axialRotation': axialRotationRange, 'zShift': zShiftRange}

# get the current working directory
cwd = os.getcwd()

# set the output file name
outputFile = cwd + '/designGeometryGrid.csv'

# set the start value for each x and crossingAngle parameter
GASrightXStart, GASrightCross = 6.5, -45
rightXStart, rightCross = 8, -45 
leftXStart, leftCross = 8, 18

# get a list of xStarts and crossStarts
xStarts = [GASrightXStart, rightXStart, leftXStart]
crossStarts = [GASrightCross, rightCross, leftCross]

# set the number of geometries to get for each region
numGeometries = 100

# get random geometry grid values for each region
df = getRandomGeometryGrid(numGeometries, ranges, xStarts, crossStarts)

# print outputDf to a csv file in the same directory as the original data file with no first column
df.to_csv(outputFile, index=False)

# incremented geometry grid
xIncrement = 0.5
crossIncrement = 5
axIncrement = 10
zIncrement = 1

# save increments to a dictionary
increments = {'xShift': xIncrement, 'crossingAngle': crossIncrement, 'axialRotation': axIncrement, 'zShift': zIncrement}
incrementDf = getSetGeometryGrid(ranges, increments, xStarts, crossStarts)
incrementDf.to_csv(cwd + '/incrementedDesignGeometryGrid.csv', index=False)