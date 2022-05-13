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
def calcSeqProportionInBin(sequence, binName, dfRep, dfFlow):
    # get sequence count in bin
    seqCount = dfRep.loc[sequence][binName]
    # get total counts of all sequences in bin
    totalAllSeqCount = dfRep[binName].sum(axis=0)
    # get percent population in bin
    percent = dfFlow.loc['Percent'][binName]
    # calculate the sequence proportion for a single bin
    binValue = percent*seqCount/totalAllSeqCount
    return binValue

# loop through all sequences and calculate the sequence proportion (numerator):
# 
def calculateNumerators(seqs, binName, dfRep, dfFlow):
    allNums = []
    for seq in seqs:
        num = calcSeqProportionInBin(seq, binName, dfRep, dfFlow)
        allNums.append(num)
    return allNums

# loops through all sequences and all bins for that sequence and calculates the reconstructed fluorescence denominator
# 
def calculateDenominators(seqs, bins, dfRep, dfFlow):
    allDenoms = []
    for seq in seqs:
        # denominator variable to hold for each sequence
        denom = 0
        for currBin in bins:
            # get sequence count in bin
            seqCount = dfRep.loc[seq][currBin]
            # get total counts of all sequences in bin
            totalAllSeqCount = dfRep[currBin].sum(axis=0)
            # get percent population in bin
            percent = dfFlow.loc['Percent'][currBin]
            # calculate the denominator for a single bin
            binValue = percent*seqCount/totalAllSeqCount
            # add to previous bin denominator total until calculated for all bins
            denom += binValue
        # append the calculated denominator to the allDenominator list
        allDenoms.append(denom)
    return allDenoms

# calculate the numerator and denominators for each bin
# 
def calculateNumeratorsAndDenominators(seqs, bins, dfRep, dfFlow):
    df = pd.DataFrame()
    # calculate the numerators
    for currBin in bins:
        binNumerators = calculateNumerators(seqs, currBin, dfRep, dfFlow)
        colName = currBin+'-Numerator'
        numColumns = len(df.columns)
        df.insert(numColumns, colName, binNumerators)
    # get the denominator for the equation 
    allDenominators = calculateDenominators(seqs, bins, dfRep, dfFlow)
    # I think I'm going to make this a new dataframe and print it out (with numerators, denominators, etc.)
    # add denominator to dataframe as a column under title Denominator
    df = df.assign(Denominator = allDenominators)
    return df

# calculate the normalized sequence contribution
def calculateNormalizedSequenceContribution(bins, df):
    dfOut = pd.DataFrame()
    for colName, binName in zip(df.columns, bins):
        if colName != 'Denominator':
            dfOut[binName] = (df[colName]/df['Denominator'])
    return dfOut

# calculate the reconstructed fluorescence value:
#
def calculateReconstructedFluorescence(bins, dfNorm, dfFlow):
    df = pd.DataFrame()
    for binName in bins:
        median = dfFlow.loc['Median'][binName]
        df[binName] = (dfNorm[binName]*median)
    sumRows = df.sum(axis=1)
    df['Fluorescence'] = sumRows
    return df

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
    