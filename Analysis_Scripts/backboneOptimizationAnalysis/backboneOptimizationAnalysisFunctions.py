# @Author: Gilbert Loiseau
# @Date:   2021-12-21
# @Filename: optimizeBackboneFunctions.py
# @Last modified by:   Gilbert Loiseau
# @Last modified time: 2022-01-07

# Multipurpose functions
"""
This file contains a list of functions that are used in the following programs:
    -
"""

import numpy as np
import pandas as pd
import re
import random as rand

from utilityFunctions import *
from plottingFunctions import *
pd.options.mode.chained_assignment = None  # default='warn'

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
            dfOutput = pd.concat([dfOutput,designSeq])
    return dfOutput


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
            dfOutput = pd.concat([dfOutput,dfRunNumber])
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
def randomlyChooseSequences(df, numStable, numClash, seed):
    stable = df[df['Total'] < 0]
    clash = df[df['Total'] > 0]
    stable = stable.sort_values(by='Total')
    #randomStable = stable.head(numStable)
    bestSequence = stable[stable['Total']==stable['Total'].min()]
    stable.drop(stable.index[stable['Total']==stable['Total'].min()], inplace=True)
    randomStable = stable.sample(n=numStable-1, random_state=seed)
    randomClash = clash.sample(n=numClash, random_state=seed)
    dfOutput = pd.concat([randomStable, randomClash, bestSequence], ignore_index=True)
    return dfOutput

# Outputs a dataframe of sequences that fall within a bin (both upper and lower bounds)
def getEnergyBin(df, bin):
    binLower, binUpper = bin
    dfOutput = df[df['Total'] >= binLower]
    dfOutput = dfOutput[dfOutput['Total'] < binUpper]
    return dfOutput

# Generates a segment filled with sequences for a CHIP
def generateSegment(df, binList, numSequences, numStable, numClash, seed):
    dfOutput = pd.DataFrame()
    # For every bin, add random sequences into a segment of a CHIP
    for bin in binList:
        tmpDf = getEnergyBin(df, bin)
        uniqueSequences = tmpDf['runNumber'].unique()
        if len(dfOutput) == 0:
            if len(uniqueSequences) < numSequences:
                for runNumber in uniqueSequences:
                    tmpDf = df[df['runNumber'] == runNumber]
                    randomSequences = randomlyChooseSequences(tmpDf, numStable, numClash, seed)
                    dfOutput = pd.concat([dfOutput,randomSequences])
            else:
                np.random.seed(seed)
                randomRunNumbers = np.random.choice(uniqueSequences, size=numSequences, replace=False)
                for runNumber in randomRunNumbers:
                    tmpDf = df[df['runNumber'] == runNumber]
                    randomSequences = randomlyChooseSequences(tmpDf, numStable, numClash, seed)
                    dfOutput = pd.concat([dfOutput,randomSequences])
        else:
            previousRunNumbers = dfOutput['runNumber'].unique()
            runNumberToChoose = np.setdiff1d(uniqueSequences, previousRunNumbers)
            np.random.seed(seed)
            randomRunNumbers = np.random.choice(runNumberToChoose, size=numSequences, replace=False)
            for runNumber in randomRunNumbers:
                tmpDf = df[df['runNumber'] == runNumber]
                randomSequences = randomlyChooseSequences(tmpDf, numStable, numClash, seed)
                dfOutput = pd.concat([dfOutput,randomSequences])
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
            dfOutput = pd.concat([dfOutput,dfRunNumber])
    except RecursionError as re:
        print("Segments for CHIP are filled!")
    return dfOutput

# function for generating a redundant library of sequences
def makeRedundantLibrary(dfMutants, dfKde, plotOutputDir, binList, numSequences, totalSegments, seed):
    dfSegments = pd.DataFrame()
    dfList = []
    for segNumber in range(1,totalSegments+1):
        dfRandomSequences = generateSegment(dfMutants, binList, numSequences, 6, 3, seed+segNumber)
        dfRandomSequences['SegmentNumber'] = segNumber
        dfSegments = pd.concat([dfSegments, dfRandomSequences])
        name = "Segment" + str(segNumber)
        dfList.append(dfRandomSequences)
        #plotKdeOverlay(dfKde, dfRandomSequences, 'Distance', 'Angle', plotOutputDir, segNumber)
    plotMultiColorKdeOverlay(dfKde, dfList, 'Distance', 'Angle', plotOutputDir, seed)
    return dfSegments

# function for generating a nonredundant library of sequences
def makeNonRedundantLibrary(df, dfKde, plotOutputDir, binList, numSequences, totalSegments, seed):
    dfSegments = pd.DataFrame()
    dfList = []
    for segNumber in range(1,totalSegments+1):
        if dfSegments.empty is True:
            dfRandomSequences = generateSegment(df, binList, numSequences, 6, 3, seed+segNumber)
            dfRandomSequences['SegmentNumber'] = segNumber
            dfSegments = pd.concat([dfSegments,dfRandomSequences])
            name = "Segment" + str(segNumber)
            dfList.append(dfRandomSequences)
        else:
            removePrevSeqList = list(set(df['runNumber'])-set(dfSegments['runNumber']))
            tmpDf = df[df['runNumber'].isin(removePrevSeqList)]
            sequenceNumbersPerBin = numberSequenceInBin(tmpDf, binList, -40)
            dfRandomSequences = generateSegment(tmpDf, binList, numSequences, 6, 3, seed+segNumber)
            dfRandomSequences['SegmentNumber'] = segNumber
            dfSegments = pd.concat([dfSegments,dfRandomSequences])
            name = "Segment" + str(segNumber)
            #plotHistogramForDataframe(dfRandomSequences, "Total", binList1, name, plotOutputDir)
            #TODO: I think I need to save the image of a plot and plot over it?
            dfList.append(dfRandomSequences)
        #plotKdeOverlay(dfKde, dfRandomSequences, 'Distance', 'Angle', plotOutputDir, seed)
    plotMultiColorKdeOverlay(dfKde, dfList, 'Distance', 'Angle', plotOutputDir, seed)
    return dfSegments

# get segments 
def getSegments(df, dfKde, plotOutputDir, redundant, binList, numSequences, totalSegments, seed):
    dfSegments = pd.DataFrame()
    if redundant is True:
        dfSegments = makeRedundantLibrary(df, dfKde, plotOutputDir, binList, numSequences, totalSegments, seed)
    else:
        dfSegments = makeNonRedundantLibrary(df, dfKde, plotOutputDir, binList, numSequences, totalSegments, seed)
    return dfSegments