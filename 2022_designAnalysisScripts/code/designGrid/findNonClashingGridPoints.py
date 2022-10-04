import sys
import os
import pandas as pd
from findNonClashingGridPointsFunc import *
from datetime import date

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
geomDict = {'xShift':{}, 'crossingAngle':{}, 'axialRotation': {}, 'zShift': {}}

# add axialRotation min, max, and increment to the dictionary
geomDict['axialRotation']['min'] = 0
geomDict['axialRotation']['max'] = 100
geomDict['axialRotation']['inc'] = 5
geomDict['zShift']['min'] = 0
geomDict['zShift']['max'] = 6
geomDict['zShift']['inc'] = 0.5
geomDict['xShift']['min'] = df['xShift'].min()
geomDict['xShift']['max'] = df['xShift'].max()
geomDict['xShift']['inc'] = 0.2
if crossingAngles[0] < 0:
    geomDict['crossingAngle']['min'] = df['crossingAngle'].max()# flip min and max for crossing angle; helps with multipurpose functions
    geomDict['crossingAngle']['max'] = df['crossingAngle'].min()
else:
    geomDict['crossingAngle']['min'] = df['crossingAngle'].min()
    geomDict['crossingAngle']['max'] = df['crossingAngle'].max()
geomDict['crossingAngle']['inc'] = 2 

acceptCutoff = 0.8
randomGeomGrid = pd.DataFrame()
numGeometries = 50
    
# make kde output dir
kdeOutputDir = outputDir + "densityPlots/"
if not os.path.exists(kdeOutputDir):
    os.makedirs(kdeOutputDir)

# setup geomGridList
geomGrid = pd.DataFrame()
# loop through unique xShifts and crossing angles plots
for xShift in df['xShift'].unique():
    # get the df for the current xShift
    xDf = df[df['xShift'] == xShift]
    for cross in xDf['crossingAngle'].unique():
        # get the df for the current crossing angle
        crossDf = xDf[xDf['crossingAngle'] == cross] 
        # plot kde for axial rotation and zShift
        outputTitle = str(xShift)+'_cross_' + str(cross)
        Z, tmpGrid = plotKde(crossDf, 'axialRotation', 'zShift', geomDict, kdeOutputDir, outputTitle)
        # add col names axialRot, zShift, and density
        tmpGrid.columns = ['axialRotation', 'zShift', 'density']
        # add xShift and crossing angle to front of the df
        tmpGrid.insert(0, 'xShift', xShift)
        tmpGrid.insert(1, 'crossingAngle', cross)
        # concat the tmpGrid to geomGrid
        geomGrid = pd.concat([geomGrid, tmpGrid], ignore_index=True)

# geometry columns
geomColumns = 'xShift,crossingAngle,axialRotation,zShift,density'.split(',')
# define random geom grid
randomGeomGrid = getRandomGeometryDf(geomGrid, numGeometries, acceptCutoff, geomDict, geomColumns)
print(randomGeomGrid)
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
designGrid = designGrid.round(4)

# write the acceptGrid to a csv file
randomGeomGrid.to_csv(outputDir + 'randomGeometryDesignGrid.csv', index=False) 
# write the designGrid to a csv file
designGrid.to_csv(outputDir + 'designGridCondorInput.csv', index=True)