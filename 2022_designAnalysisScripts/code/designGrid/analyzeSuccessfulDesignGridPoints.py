import sys
import os
import pandas as pd
from designGridFunctions import *

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

# sample
sample = 'left'

# get the column names
cols = 'xShift,crossingAngle,axialRotation,zShift'.split(',')
outputFile = cwd + '/designGeometryGrid_'+sample+'.csv'

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
    # set the output file name
    outputFile = cwd + '/designGeometryGrid_'+sample+'.csv'
    # write the output file
    outputDf.to_csv(outputFile, index=False)
    # TODO: the below doesn't work; fix
    df = pd.concat([df, outputDf])

# bin data
#xBins = np.arange(6.5, 7.5, 0.1)
#crossBins = np.arange(, , 5)

# get the min and max of the xShift 
xMin = df['xShift'].min()
xMax = df['xShift'].max()
crossMin = df['crossingAngle'].min()
crossMax = df['crossingAngle'].max()

# get the df for min and max xShift
dfXMin = df[df['xShift'] == xMin]
dfXMax = df[df['xShift'] == xMax]

# plot geometry density plot for xShift and crossingAngle
#plotKde(df, 'xShift', 'crossingAngle', xMin, xMax, crossMin, crossMax, cwd, sample)

# get the list of crossing angles
crossingAngles = np.arange(crossMin, crossMax+2, crossInc)

# loop through crossingAngle and xShift values
for cross in crossingAngles:
    tmpDf = df[df['crossingAngle'] == cross]
    # plot kde for axial rotation and zShift
    outputTitle = sample+'_cross_' + str(cross)
    plotKde(tmpDf, 'axialRotation', 'zShift', -100, 0, 0, 6, cwd, outputTitle)

minOut = sample+"_"+str(xMin)
maxOut = sample+"_"+str(xMax)
plotKde(dfXMin, 'axialRotation', 'zShift', -100, 0, 0, 6, cwd, minOut)
plotKde(dfXMax, 'axialRotation', 'zShift', -100, 0, 0, 6, cwd, maxOut)