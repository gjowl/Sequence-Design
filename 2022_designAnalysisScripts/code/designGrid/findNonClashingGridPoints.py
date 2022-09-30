import sys
import os
import pandas as pd
from findNonClashingGridPointsFunc import *
from datetime import date

# get the input directory
inputDir = sys.argv[2]

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

# get the column names
cols = 'xShift,crossingAngle,axialRotation,zShift,energy'.split(',')
outputFile = outputDir + 'designGeometryGrid.csv'

df = pd.DataFrame()
# check if output file exists
if os.path.isfile(outputFile):
    # read in the file
    df = pd.read_csv(outputFile)
else:
    getNonClashingGeometryData(inputDir, outputFile, cols)

# get the min and max of the xShift 
xMin = df['xShift'].min()
xMax = df['xShift'].max()
crossMin = df['crossingAngle'].min()
crossMax = df['crossingAngle'].max()

# plot geometry density plot for xShift and crossingAngle
#plotKde(df, 'xShift', 'crossingAngle', xMin, xMax, xInc, crossMin, crossMax, crossInc, outputDir, inputDirName)

# get absolute value of axial rotation
df['axialRotation'] = df['axialRotation'].abs()# I'm running the negatives, but this just makes it more viewable

# adjust axial rot and zShift to the input values from 0-100(ax) and 0-6(z)
adjustedAxialRot = (10*df['axialRotation']/9)-(200*df['zShift']/27)
adjustedZShift = (10/9*df['zShift'])-(0.15*df['axialRotation']/9)
df['axialRotation'] = round(adjustedAxialRot, 2)
df['zShift'] = round(adjustedZShift, 2)

# get the list of crossing angles
crossingAngles = np.arange(crossMin, crossMax+2, crossInc)

# get the df for min and max xShift
dfXMin = df[df['xShift'] == xMin]
dfXMax = df[df['xShift'] == xMax]

# add in a dictionary for axialRotation and zShift
valuesDict = {'axialRotation': {}, 'zShift': {}}

# add axialRotation min, max, and increment to the dictionary
axAndZDict['axialRotation']['min'] = 0
axAndZDict['axialRotation']['max'] = 100
axAndZDict['zShift']['min'] = 0
axAndZDict['zShift']['max'] = 6

minOut = str(xMin)
maxOut = str(xMax)
plotKde(dfXMin, 'axialRotation', 'zShift', axAndZDict, acceptCutoff, outputDir, minOut)
plotKde(dfXMax, 'axialRotation', 'zShift', axAndZDict, acceptCutoff, outputDir, maxOut)

# add df for min and max xShift to list
dfList = [dfXMin, dfXMax]
outputList = [minOut, maxOut]
# loop through crossingAngle and xShift values
for df, out in zip(dfList,outputList):
    for cross in crossingAngles:
        tmpDf = df[df['crossingAngle'] == cross]
        # plot kde for axial rotation and zShift
        outputTitle = out+'_cross_' + str(cross)
        Z = plotKde(tmpDf, 'axialRotation', 'zShift', axAndZDict, accceptCutoff, outputDir, outputTitle)
        xAxis = df['axialRotation']
        yAxis = df['zShift']
        data = df['energy']
        dataColumn = 'energy'
        plotKdeOverlay(Z, xAxis, 0, 100, yAxis, 0, 6, data, dataColumn, outputDir, outputTitle)