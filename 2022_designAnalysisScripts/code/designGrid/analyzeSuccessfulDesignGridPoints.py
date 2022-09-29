import sys
import os
import pandas as pd
from designGridFunctions import *
from datetime import date

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
cols = 'xShift,crossingAngle,axialRotation,zShift'.split(',')
outputFile = outputDir + 'designGeometryGrid.csv'

df = pd.DataFrame()
# check if output file exists
if os.path.isfile(outputFile):
    # read in the file
    df = pd.read_csv(outputFile)
else:
    # setup output dataframe
    outputDf = pd.DataFrame(columns=cols)
    # loop through the files in the input directory
    for file in os.listdir(inputDir):
        # check to see if the file is a pdb file
        if file.endswith('.pdb'):
            # remove the .pdb extension
            file = file[:-4]
            # split file by "_"
            splitFile = file.split('_')
            # get xShift, crossingAngle, axialRotation, and zShift
            xShift, crossingAngle, axialRotation, zShift = splitFile[0], splitFile[1], splitFile[2], splitFile[3]
            # keep only numbers
            xShift = xShift.replace('x', '')
            crossingAngle = crossingAngle.replace('cross', '')
            axialRotation = axialRotation.replace('ax', '')
            zShift = zShift.replace('z', '')
            # convert to float
            xShift = float(xShift)
            crossingAngle = float(crossingAngle)
            axialRotation = float(axialRotation)
            zShift = float(zShift)
            #print(xShift, crossingAngle, axialRotation, zShift)
            # add to a dataframe
            outputDf = pd.concat([outputDf, pd.DataFrame([[xShift, crossingAngle, axialRotation, zShift]], columns=cols)])
    # write the output file
    outputDf.to_csv(outputFile, index=False)
    # save the output dataframe to df
    df = outputDf

# get the min and max of the xShift 
xMin = df['xShift'].min()
xMax = df['xShift'].max()
crossMin = df['crossingAngle'].min()
crossMax = df['crossingAngle'].max()

# plot geometry density plot for xShift and crossingAngle
plotKde(df, 'xShift', 'crossingAngle', xMin, xMax, xInc, crossMin, crossMax, crossInc, outputDir, inputDirName)

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

minOut = str(xMin)
maxOut = str(xMax)
plotKde(dfXMin, 'axialRotation', 'zShift', 0, 100, axInc, 0, 6, zInc, outputDir, minOut)
plotKde(dfXMax, 'axialRotation', 'zShift', 0, 100, axInc, 0, 6, zInc, outputDir, maxOut)

# add df for min and max xShift to list
dfList = [dfXMin, dfXMax]
outputList = [minOut, maxOut]
# loop through crossingAngle and xShift values
for df, out in zip(dfList,outputList):
    for cross in crossingAngles:
        tmpDf = df[df['crossingAngle'] == cross]
        # plot kde for axial rotation and zShift
        outputTitle = out+'_cross_' + str(cross)
        plotKde(tmpDf, 'axialRotation', 'zShift', 0, 100, axInc, 0, 6, zInc, outputDir, outputTitle)