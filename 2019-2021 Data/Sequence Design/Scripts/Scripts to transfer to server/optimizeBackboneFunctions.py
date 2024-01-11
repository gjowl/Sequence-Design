# @Author: Gilbert Loiseau
# @Date:   2021-12-21
# @Filename: optimizeBackboneFunctions.py
# @Last modified by:   Gilbert Loiseau
# @Last modified time: 2021-12-24



from datetime import date
from scipy import stats
from matplotlib import gridspec
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import re
import seaborn as sns
import logomaker as lm
import random as rand

# Multipurpose functions
# gets the first bin using lowest value in dataframe and minimum bin value given
def getFirstBin(df, binMin, colName):
    minValue = df[colName].min()
    bin = [minValue, binMin]
    return bin

# generates a list of bins based on given minimum, maximum, and width of desired bins
def getBins(df, colName, binMin, binMax, binWidth):
    binList = []
    firstBin = getFirstBin(df, binMin, colName)
    binList.append(firstBin)
    while binMin < binMax:
        nextBin = binMin+binWidth
        bins = [binMin, nextBin]
        binMin = nextBin
        binList.append(bins)
    return binList

# Plot histogram for dataframe and a given list of bins
def plotHistogramForDataframe(df, colName, binList, filename, outputDir):
    fig, ax = plt.subplots()
    df.hist(column=colName, bins=binList, figsize=(25,25), color='purple')
    title = filename
    plt.title(title)
    plt.savefig(outputDir+"_"+filename+"_"+colName+".png", bbox_inches='tight', dpi=150)
    plt.close()

# plot 2d scatterplot for a given dataframe and two columns
def plotScatterplotForDataframe(df, xColumnName, yColumnName, filename):
    fig, ax = plt.subplots()
    plt.xticks(ticks=df[xColumnName].unique())
    plt.scatter(x=df[xColumnName], y=df[yColumnName], s=0.3)
    plt.title(title)
    plt.savefig(outputDir+filename+".png", bbox_inches='tight', dpi=150)
    plt.close()

# Prints out the number of sequences within each segment of the CHIP
def outputNumberSequencesInEachSegment(df):
    for segNumber in df['SegmentNumber'].unique():
        dfSegNumber = df[df['SegmentNumber'] == segNumber]
        print('Segment #', segNumber, ": ", len(dfSegNumber))

# Adds in sequences from the original design sequence dataframe into the filled mutants segment dataframe
def getDesignSequencesForSegment(df, dfSegments):
    dfOutput = pd.DataFrame()
    for runNumber in dfSegments['runNumber'].unique():
        dfRunNumber = dfSegments[dfSegments['runNumber'] == runNumber]
        for segNumber in dfRunNumber['SegmentNumber'].unique():
            designSeq = df[df['runNumber'] == runNumber]
            designSeq['SegmentNumber'] = segNumber
            dfOutput = dfOutput.append(designSeq)
    return dfOutput


# Plot angle vs distance density plot for dataframe values
def plotKdeOverlay(dfKde, df, xAxis, yAxis, outputDir, num):
    #Variable set up depending on data that I'm running
    xmin = 6
    xmax = 12
    ymin = -100
    ymax = 100
    X, Y = np.mgrid[xmin:xmax:24j, ymin:ymax:40j]
    x = dfKde.loc[:, xAxis]
    y = dfKde.loc[:, yAxis]

    #Kernel Density Estimate Calculation
    positions = np.vstack([X.ravel(), Y.ravel()])
    values = np.vstack([x, y])
    kernel = stats.gaussian_kde(values)
    kernel.set_bandwidth(bw_method='silverman')
    Z = np.reshape(kernel(positions).T, X.shape)

    # Setup for plotting code
    fig, ax = plt.subplots()
    plt.rc('font', size=10)
    plt.rc('xtick', labelsize=10)
    plt.rc('ytick', labelsize=10)

    xData = df['xShift']
    yData = df['crossingAngle']
    title = "Segment #"+str(num)
    filename = str(num)+"_Segment"
    plotOverlay(Z, title, filename, xAxis, yAxis, xmax, xmin, ymax, ymin, xData, yData, outputDir)
    plotContour(dfKde, title, filename, xAxis, yAxis, xmax, xmin, ymax, ymin, xData, yData, outputDir)
    plt.close()

# Parse the sequences only accepting geometries with at least x clashing and y stable mutants
def checkForClashAndStable(df, numStable, numClash):
    dfOutput = pd.DataFrame()
    for runNumber in df['runNumber'].unique():
        dfRunNumber = df[df['runNumber'] == runNumber]
        dfClash = dfRunNumber[dfRunNumber['Total'] > 0]
        dfStable = dfRunNumber[dfRunNumber['Total'] < 0]
        clash = len(dfClash)
        stable = len(dfStable)
        if clash >= numClash and stable >= numStable:
            dfOutput = dfOutput.append(dfRunNumber)
    return dfOutput


# counts the number of sequences within bins in a given dataframe; outputs a list of lists
def numberSequenceInBin(df, binList, lowBin):
    binTotals = []
    for binLower, binUpper in binList:
        tmpDf = df[df['Total'] >= binLower]
        tmpDf = tmpDf[tmpDf['Total'] < binUpper]
        numSequences = len(tmpDf['runNumber'].unique())
        binTotals.append(numSequences)
    return binTotals

# Gets sequences from a dataframe, randomly choosing based on the given number of stable and clashing; always accept the best stable sequence
def randomlyChooseSequences(df, numStable, numClash):
    stable = df[df['Total'] < 0]
    clash = df[df['Total'] > 0]
    stable = stable.sort_values(by='Total')
    #randomStable = stable.head(numStable)
    bestSequence = stable[stable['Total']==stable['Total'].min()]
    stable.drop(stable.index[stable['Total']==stable['Total'].min()], inplace=True)
    randomStable = stable.sample(n=numStable-1)
    randomClash = clash.sample(n=numClash)
    dfOutput = pd.concat([randomStable, randomClash, bestSequence], ignore_index=True)
    return dfOutput

# Outputs a dataframe of sequences that fall within a bin (both upper and lower bounds)
def getEnergyBin(df, bin):
    binLower, binUpper = bin
    dfOutput = df[df['Total'] >= binLower]
    dfOutput = dfOutput[dfOutput['Total'] < binUpper]
    return dfOutput

# Generates a segment filled with sequences for a CHIP
def generateSegment(df, binList, numSequences, numStable, numClash):
    dfOutput = pd.DataFrame()
    # For every bin, add random sequences into a segment of a CHIP
    for bin in binList:
        tmpDf = getEnergyBin(df, bin)
        uniqueSequences = tmpDf['runNumber'].unique()
        if len(dfOutput) == 0:
            if len(uniqueSequences) < numSequences:
                for runNumber in uniqueSequences:
                    tmpDf = df[df['runNumber'] == runNumber]
                    randomSequences = randomlyChooseSequences(tmpDf, numStable, numClash)
                    dfOutput = dfOutput.append(randomSequences)
            else:
                randomRunNumbers = np.random.choice(uniqueSequences, size=numSequences, replace=False)
                for runNumber in randomRunNumbers:
                    tmpDf = df[df['runNumber'] == runNumber]
                    randomSequences = randomlyChooseSequences(tmpDf, numStable, numClash)
                    dfOutput = dfOutput.append(randomSequences)
        else:
            previousRunNumbers = dfOutput['runNumber'].unique()
            runNumberToChoose = np.setdiff1d(uniqueSequences, previousRunNumbers)
            randomRunNumbers = np.random.choice(runNumberToChoose, size=numSequences, replace=False)
            for runNumber in randomRunNumbers:
                tmpDf = df[df['runNumber'] == runNumber]
                randomSequences = randomlyChooseSequences(tmpDf, numStable, numClash)
                dfOutput = dfOutput.append(randomSequences)
    return dfOutput

## Below functions are redacted, but I thought they were interesting to keep
def checkIfMoreThanMaxAllowed(df, dfToCheck, numSegments, segmentNumber, maxNumberPerSegment):
    if dfToCheck.empty is True:
        return segmentNumber
    numberToAdd = len(df)
    dfTotal = dfToCheck[dfToCheck['SegmentNumber'] == segmentNumber]
    total = len(dfTotal)+numberToAdd
    if total > maxNumberPerSegment:
        segmentNumber = rand.randint(1, numSegments)
        segmentNumber = checkIfMoreThanMaxAllowed(df, dfToCheck, numSegments, segmentNumber, maxNumberPerSegment)
        return segmentNumber
    else:
        return segmentNumber

def assignSequencesToSegments(df, numSegments, maxNumberPerSegment):
    dfOutput = pd.DataFrame()
    try:
        for runNumber in df['runNumber'].unique():
            dfRunNumber = df[df['runNumber'] == runNumber]
            segmentNumber = rand.randint(1,numSegments)
            segmentNumber = checkIfMoreThanMaxAllowed(dfRunNumber, dfOutput, numSegments, segmentNumber, maxNumberPerSegment)
            dfRunNumber['SegmentNumber'] = segmentNumber
            dfOutput = dfOutput.append(dfRunNumber)
    except RecursionError as re:
        print("Segments for CHIP are filled!")
    return dfOutput
