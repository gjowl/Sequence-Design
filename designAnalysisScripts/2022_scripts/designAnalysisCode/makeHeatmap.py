import os, sys, pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def heatmapOutput(df, outputDir, region, yAxis, xAxis, cols):
    for col in cols:
        # keep only the columns we want
        piv = pd.pivot_table(df, values=[col, 'NumSeqs'], index=[yAxis], columns=[xAxis])
        # using sns, plot the data as a heatmap with the number of sequences in each bin
        sns.heatmap(piv[col])
        # save the figure
        plt.savefig(f'{outputDir}/{region}/heatmap_{col}_{xAxis}.png')
        plt.close()
        # using sns, plot the data as a heatmap with the number of sequences in each bin
        sns.heatmap(piv[col], annot=piv['NumSeqs'])
        # save the figure
        plt.savefig(f'{outputDir}/{region}/heatmap_{col}_{xAxis}_numSeqs.png')
        plt.close()

def getAverageEnergyPerRegionDivision(inputDf, yAxis, xAxis, binSizeMap):
    outputDf = pd.DataFrame()
    # get the lowest angle and xShift values
    lowestY = round(df_region[yAxis].min())
    lowestX = df_region[xAxis].min().round(1)
    # define the bin size
    yBinSize, xBinSize = binSizeMap[yAxis], binSizeMap[xAxis]
    # create a list of angles and xShifts
    yAxisList = list(range(int(lowestY), int(lowestY)+yBinSize*10, yBinSize))
    # create a float list of xShifts
    xAxisList = list(np.arange(lowestX, lowestX+xBinSize*10, xBinSize))
    for yStart in yAxisList:
        for xStart in xAxisList:
            df = pd.DataFrame()
            # get the average hbond difference for crossingAngles between -50 and -48
            df = df_region[df_region[yAxis] > yStart]
            df = df[df[yAxis] < yStart+yBinSize]
            df = df[df[xAxis] > xStart]
            df = df[df[xAxis] < xStart+xBinSize]
            # define the crossing angle
            df[yAxis] = yStart
            df[xAxis] = round(xStart, 1)
            # get the average energy differences
            df['HBOND'], df['VDW'], df['IMM1'], df['NumSeqs'] = df['HBONDDiff'].mean(), df['VDWDiff'].mean(), df['IMM1Diff'].mean(), len(df.index)
            outputDf = pd.concat([outputDf, df])
    return outputDf

# read in the datafile from command line
dataFile = sys.argv[1]
outputDir = sys.argv[2]

# read in the datafile as a dataframe
inputDf = pd.read_csv(dataFile, sep=',', header=0, dtype={'Interface': str})

angleImplementer = 2
xShiftImplementer = 0.2
cols = ['HBOND', 'VDW', 'IMM1']
yAxis = 'endCrossingAngle'
xAxisList = 'endXShift', 'endAxialRotation', 'endZShift'
binSizeMap = {'endCrossingAngle': 2, 'endXShift': 0.2, 'endAxialRotation': 10, 'endZShift': 0.5}
for xAxis in xAxisList:
    # loop through the unique regions
    for region in inputDf['Region'].unique():
        df_region = inputDf[inputDf['Region'] == region]
        # loop through the crossing angles
        outputDf = getAverageEnergyPerRegionDivision(inputDf, yAxis, xAxis, binSizeMap)
        heatmapOutput(outputDf, outputDir, region, yAxis, xAxis, cols)