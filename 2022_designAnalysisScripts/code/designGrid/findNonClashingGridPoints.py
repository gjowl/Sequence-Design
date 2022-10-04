import sys
import os
import pandas as pd
from findNonClashingGridPointsFunc import *
from datetime import date
import random as rand

# get the input directory
inputDir = sys.argv[1]

# get current working directory
cwd = os.getcwd() + "/"

# get the date
today = date.today()
today = today.strftime("%Y_%m_%d")

# get the name of the input directory
inputDirName = os.path.basename(os.path.normpath(inputDir))
# remove the date from the input directory name
inputDirName = inputDirName.split("_")[1]

# get the output directory
outputDir = cwd + today + "_adjustedAxAndZGridData/" + inputDirName + "/"

# make the output directory if it doesn't exist
if not os.path.exists(outputDir):
    os.makedirs(outputDir)

# hardcoded column names
cols = 'xShift,crossingAngle,axialRotation,zShift,energy'.split(',')
outputFile = outputDir + 'designGeometryGrid.csv'

df = pd.DataFrame()
# check if output file doesn't exist
if not os.path.exists(outputFile):
    getNonClashingGeometryData(inputDir, outputFile, cols)

# read the output file into a dataframe
df = pd.read_csv(outputFile)

# plot geometry density plot for xShift and crossingAngle
#plotKde(df, 'xShift', 'crossingAngle', xMin, xMax, xInc, crossMin, crossMax, crossInc, outputDir, inputDirName)

# adjust axial rot and zShift to the input values from 0-100(ax) and 0-6(z)
adjustedAxialRot = (10*df['axialRotation']/9)+(200*df['zShift']/27)
# add 100 to the adjusted axial rotation
adjustedAxialRot = adjustedAxialRot + 100
adjustedZShift = (10/9*df['zShift'])+(0.15*df['axialRotation']/9)
df['axialRotation'] = round(adjustedAxialRot, 2)
df['zShift'] = round(adjustedZShift, 2)

# get the min and max of xShift and a list of the crossing angles
dfXMin, dfXMax = getDfMinAndMax(df, 'xShift')

# get a list of crossing angles from df
crossingAngles = df['crossingAngle'].unique()

# add in a dictionary for axialRotation and zShift
axAndZDict = {'axialRotation': {}, 'zShift': {}}

# add axialRotation min, max, and increment to the dictionary
axAndZDict['axialRotation']['min'] = 0
axAndZDict['axialRotation']['max'] = 100
axAndZDict['zShift']['min'] = 0
axAndZDict['zShift']['max'] = 6

# add df for min and max xShift to list
dfList = [dfXMin, dfXMax]
min, max = dfXMin['xShift'].values[0], dfXMax['xShift'].values[0]
xShifts = [min, max]
acceptCutoff = 0.8
randomGeomGrid = pd.DataFrame()
numGeometries = 3

# loop through crossingAngle and xShift values
for df, xShift in zip(dfList,xShifts):
    for cross in crossingAngles:
        tmpDf = df[df['crossingAngle'] == cross]
        # plot kde for axial rotation and zShift
        outputTitle = str(xShift)+'_cross_' + str(cross)
        Z, tmpGrid = plotKde(tmpDf, 'axialRotation', 'zShift', axAndZDict, acceptCutoff, outputDir, outputTitle)
        # add col names axialRot, zShift, and density
        tmpGrid.columns = ['axialRotation', 'zShift', 'density'] 
        # pick x random geometries from the acceptGrid
        for i in range(0,numGeometries):
            randRow = tmpGrid.sample(n=1)
            # get a random float between -5 and +5
            randAxFloat = rand.uniform(-5,5)
            # add the random float to the axial rotation
            randRow['axialRotation'] = randRow['axialRotation'] + randAxFloat
            if randRow['axialRotation'].values[0] >100:
                randRow['axialRotation'] = 100
            if randRow['axialRotation'].values[0] <0:
                randRow['axialRotation'] = 0
            # get a random float between -0.5 and +0.5
            randZFloat = rand.uniform(-0.5,0.5)
            # add the random float to the zShift
            randRow['zShift'] = randRow['zShift'] + randZFloat
            if randRow['zShift'].values[0] >6:
                randRow['zShift'] = 6
            if randRow['zShift'].values[0] <0:
                randRow['zShift'] = 0
            # get a crossing angle within 2 of the crossing angle and within the range of allowed crossing angles
            randCross = rand.uniform(cross-2, cross+2)
            # if the crossing angle is greater than -35, set it to -35
            if randCross < 0:
                if randCross > -35:
                    randCross = -35
                # if the crossing angle is less than -45, set it to -45
                if randCross < -45:
                    randCross = -45
            else:
                if randCross < 18:
                    randCross = 18
                if randCross > 28:
                    randCross = 28
            # get a xShift within xShift range
            # check if xShift is the lower value in xShifts list
            if xShift == xShifts[0]:
                randXShift = rand.uniform(xShift, xShift+0.5)
            else:
                randXShift = rand.uniform(xShift-0.5, xShift)
            # add randXShift and randCross to the front of randRow
            randRow.insert(0, 'crossingAngle', randCross)
            randRow.insert(0, 'xShift', randXShift)
            # add the random row to the randomGrid
            randomGeomGrid = pd.concat([randomGeomGrid, randRow], ignore_index=True)

# convert grid to input csv for design run
designGrid = randomGeomGrid.copy()
# get first crossing angle
cross = designGrid['crossingAngle'].values[0]
# check if negative crossing angle
if cross < 0:
    designGrid['negCross'] = 'true'
    designGrid['interface'] = '000110011001100110000'
else:
    designGrid['negCross'] = 'false'
    designGrid['interface'] = '000011011001101100000'
designGrid['crossingAngle'] = abs(designGrid['crossingAngle'])
designGrid['negRot'] = 'true'
# pop the negCross and negRot columns
negCross = designGrid.pop('negCross')
negRot = designGrid.pop('negRot')
# get the index of the crossing angle column
crossIndex = designGrid.columns.get_loc('crossingAngle')
# put the negCross column right after the crossingAngle column
designGrid.insert(crossIndex+1, 'negCross', negCross)
# get index of the axial rotation column
axIndex = designGrid.columns.get_loc('axialRotation')
# put the negRot column right after the axialRotation column
designGrid.insert(axIndex+1, 'negRot', negRot)

# round all values to 2 decimal places
designGrid = designGrid.round(3)

# write the acceptGrid to a csv file
randomGeomGrid.to_csv(outputDir + 'randomGeometryDesignGrid.csv', index=False) 
# write the designGrid to a csv file
designGrid.to_csv(outputDir + 'designGridCondorInput.csv', index=True)