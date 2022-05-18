import sys
import helper
import statistics as stat
from functions import *

# reconstructed fluorescence variables
"""
From input file
i = the sequence in AA format
j = current bin number
c = the number of a sequence counted within the bin

From sorter
f = fraction of the entire population (as a percent from sorting) found within the bin 
m = median fluorescence of the sorted bin

Reconstructed fluorescence
a = fluorescence in current bin
p = average fluorescence 
"""
# TODO: add in all of the math parts as descriptions below
# sequence proportion:
# 
def calcSeqProportionInBin(sequence, totalAllSeqCount, binName, dfRep, dfFlow):
    # get sequence count in bin
    seqCount = dfRep.loc[sequence][binName]
    # get percent population in bin
    percent = dfFlow.loc['Percent'][binName]
    # calculate the sequence proportion for a single bin
    binValue = percent*seqCount/totalAllSeqCount
    return binValue

# loop through all sequences and calculate the sequence proportion (numerator):
# 
def calculateNumerators(seqs, inputFile, binName, dfRep, dfFlow):
    allNums = []
    # get total counts of all sequences in bin
    #TODO: fix this so the header is the names 
    dfCount = pd.read_csv(inputFile, delimiter='\t', header=None, skiprows=range(0,3), nrows=1)
    goodSeqCount = dfCount.iloc[:,4][0]
    totalAllSeqCount = dfCount.iloc[:,0]
    for seq in seqs:
        num = calcSeqProportionInBin(seq, goodSeqCount, binName, dfRep, dfFlow)
        allNums.append(num)
    return allNums

# calculate the denominator for reconstructed fluorescence calculation
def calculateDenominatorsForSequence(seqCount, goodSeqCount, totalSeqCount, currBin, dfFlow):
    # get percent population in bin
    percent = dfFlow.loc['Percent'][currBin]
    # calculate the denominator for a single bin
    goodSeqDenom = percent*seqCount/goodSeqCount
    totalSeqDenom = percent*seqCount/totalSeqCount
    return goodSeqDenom, totalSeqDenom

# get the counts that can be used for good seqs and total seqs:
# 
def getGoodSeqAndTotalSeqCounts(inputDir, currBin):
    inputFile = inputDir + currBin+'.txt'
    dfCount = pd.read_csv(inputFile, delimiter='\t', header=None, skiprows=range(0,3), nrows=1)
    goodSeqCount = dfCount.iloc[:,4][0]
    totalAllSeqCount = dfCount.iloc[:,0][0]
    return goodSeqCount, totalAllSeqCount

# loops through all sequences and all bins for that sequence and calculates the reconstructed fluorescence denominator
# 
def calculateDenominators(seqs, inputDir, bins, dfRep, dfFlow):
    goodSeqDenoms = []
    allSeqDenoms = []
    for seq in seqs:
        # denominator variable to hold for each sequence
        sumDenomGood = 0
        sumDenomAll = 0
        for currBin in bins:
            # get total counts of all sequences in bin
            goodSeqCount, totalSeqCount = getGoodSeqAndTotalSeqCounts(inputDir, currBin)
            # get sequence count in bin
            seqCount = dfRep.loc[seq][currBin]
            # calculate the denominator for the sequence
            goodSeqDenominator, totalSeqDenominator = calculateDenominatorsForSequence(seqCount, goodSeqCount, totalSeqCount, currBin, dfFlow)
            # add to previous bin denominator total until calculated for all bins
            sumDenomGood += goodSeqDenominator
            sumDenomAll += totalSeqDenominator
        # append the calculated denominator to the allDenominator list
        goodSeqDenoms.append(sumDenomGood)
        allSeqDenoms.append(sumDenomAll)
    return goodSeqDenoms, allSeqDenoms

# calculate the numerator and denominators for each bin
def calculateNumeratorsAndDenominators(seqs, inputDir, bins, dfRep, dfFlow):
    df = pd.DataFrame()
    # calculate the numerators
    for currBin in bins:
        inputFile = inputDir + currBin+'.txt'
        binNumerators = calculateNumerators(seqs, inputFile, currBin, dfRep, dfFlow)
        colName = currBin+'-Numerator'
        numColumns = len(df.columns)
        df.insert(numColumns, colName, binNumerators)
    # get the denominator for the equation 
    goodSeqDenominators, allSeqDenominators = calculateDenominators(seqs, inputDir, bins, dfRep, dfFlow)
    # I think I'm going to make this a new dataframe and print it out (with numerators, denominators, etc.)
    # add denominator to dataframe as a column under title Denominator
    df = df.assign(GoodSeqDenominator = goodSeqDenominators)
    df = df.assign(TotalSeqDenominator = allSeqDenominators)
    return df

# calculate the normalized sequence contribution
def calculateNormalizedSequenceContribution(bins, df):
    dfGood = pd.DataFrame()
    dfTotal = pd.DataFrame()
    for colName, binName in zip(df.columns, bins):
        if 'Denominator' not in colName:
            dfGood[binName] = (df[colName]/df['GoodSeqDenominator'])
            dfTotal[binName] = (df[colName]/df['TotalSeqDenominator'])
    return dfGood, dfTotal

# calculate the reconstructed fluorescence value:
# p = average fluorescence
def calculateReconstructedFluorescence(bins, dfNormGood, dfNormTotal, dfFlow):
    dfGood = pd.DataFrame()
    dfTotal = pd.DataFrame()
    for binName in bins:
        median = dfFlow.loc['Median'][binName]
        dfGood[binName] = (dfNormGood[binName]*median)
        dfTotal[binName] = (dfNormTotal[binName]*median)
    sumRowsGood = dfGood.sum(axis=1)
    sumRowsTotal = dfTotal.sum(axis=1)
    dfGood['Fluorescence'] = sumRowsGood
    dfTotal['Fluorescence'] = sumRowsTotal
    return dfGood, dfTotal

# insert column at the end of the dataframe
def insertAtEndOfDf(df, colName, col):
    numCol = len(df.columns)
    df.insert(numCol, colName, col)
    return df

# get average, stDev, etc. from reconstructed fluorescence
def outputReconstructedFluorescenceDf(df):
    colNames = df.columns
    avgFluors = []
    stdDevFluors = []
    for index, row in df.iterrows():
        fluorVals = []
        repsWithSequence = 0
        for col in colNames:
            fluor = row[col]
            if fluor != 0:
                fluorVals.append(fluor)
        if len(fluorVals) > 1:
            avgFluor = stat.mean(fluorVals)
            stdDevFluor = stat.stdev(fluorVals)
            avgFluors.append(avgFluor)
            stdDevFluors.append(stdDevFluor)
        elif len(fluorVals) == 1:
            avgFluors.append(fluorVals[0])
            stdDevFluors.append(0)
        else:
            avgFluors.append(0)
            stdDevFluors.append(0)
    df = insertAtEndOfDf(df, 'Average', avgFluors)
    df = insertAtEndOfDf(df, 'StdDev', stdDevFluors)
    return df