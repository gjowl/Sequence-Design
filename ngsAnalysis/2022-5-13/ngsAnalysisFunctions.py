import sys
import helper
import numpy as np
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
# helper function that will add in the sequences and segments as columns before creating csv
def outputAnalysisDfToCsv(df, seqs, segments, outputDir, name):
    # output dataframe to csv file and add sequence id lists
    df.insert(0, 'Sequence', seqs)
    df.insert(1, 'Segments', segments)
    filename = outputDir+name
    df.to_csv(filename)



#FLUORESCENCE RECONSTRUCTION
# main function for fluorescence reconstruction
def reconstructFluorescenceForDfList(dfToReconstruct, reconstructionDirList, inputDir, dfFlow, seqs, segments, numReplicates, usePercentOptionList):
    # loop through the lists of reconstruction dfs, dirs, and percent options (these should all be the same length)
    # list of dfs
    list_df = []
    for df, outputDir, usePercent in zip(dfToReconstruct, reconstructionDirList, usePercentOptionList):
        # if the dir is empty, continue
        if len(os.listdir(outputDir)) < 1:
            dfBins = df.filter(like='C')
            # reconstruct the fluorescence for both good and total sequence numbers
            df_good, df_total = getReconstructedFluorescenceDf(numReplicates, dfBins, seqs, segments, inputDir, outputDir, dfFlow, usePercent)
            outputAnalysisDfToCsv(df_good, seqs, segments, outputDir, 'avgFluorGoodSeqs.csv') 
            outputAnalysisDfToCsv(df_total, seqs, segments, outputDir, 'avgFluorTotalSeqs.csv') 
            list_df.append(df_good)
            list_df.append(df_total)
        else:
            print(outputDir, "files already made. If want to remake, make sure the directory is empty.\n")
            print("Loading files...\n")
            df_good    = pd.read_csv(outputDir+'avgFluorGoodSeqs.csv')
            df_total   = pd.read_csv(outputDir+'avgFluorTotalSeqs.csv')
            list_df.append(df_good)
            list_df.append(df_total)
            print("Done loading fluorescence reconstruction files into dataframes!\n")
    return list_df

# use below functions to calculate the reconstructed fluorescence for
# each sequence and add it to dataframes
def getReconstructedFluorescenceDf(numReplicates, dfBins, seqs, segments, inputDir, outputDir, dfFlow, usePercents=False):
    # initialize dataframe for the calculations using the good and total seq counts
    dfAvgGood = pd.DataFrame()
    dfAvgTotal = pd.DataFrame()
    # loop until going through all replicates
    i = 1
    # Hardcoded output file names:
    normalizationFile = 'norm'
    rawFluorFile = 'rawFluor'
    while i <= numReplicates:
        # TODO: get this working initialize df to hold all dfs for output
        list_df = []
        # get replicate number
        replicate = 'Rep'+str(i)
        # filter out anything that isn't the same replicate
        dfRep = dfBins.filter(like=replicate)
        # get all hour marks names for this replicate
        colNames = dfRep.columns
        # add in sequence column to first column, then convert to index
        dfRep.insert(0, 'Sequence', seqs)
        dfRep = dfRep.set_index('Sequence')
        # get a dataframe with numerators and denominators
        dfGoodNumDenom, dfTotalNumDenom = calculateNumeratorsAndDenominators(seqs, inputDir, colNames, dfRep, dfFlow, usePercents)
        # output a dataframe of a values for each sequence for each bin
        dfNormGood, dfNormTotal = calculateNormalizedSequenceContribution(colNames, dfGoodNumDenom, dfTotalNumDenom)
        goodNorm = normalizationFile+replicate+'Good.csv'
        totalNorm = normalizationFile+replicate+'Total.csv'
        # calculate the final reconstructed fluorescence
        dfFluorGood, dfFluorTotal = calculateReconstructedFluorescence(colNames, dfNormGood, dfNormTotal, dfFlow)
        goodRawFile = rawFluorFile+replicate+'Good.csv'
        totalRawFile = rawFluorFile+replicate+'Total.csv'
        # write to output file for each replicate
        outputAnalysisDfToCsv(dfNormGood, seqs, segments, outputDir, goodNorm)
        outputAnalysisDfToCsv(dfNormTotal, seqs, segments, outputDir, totalNorm)
        outputAnalysisDfToCsv(dfFluorGood, seqs, segments, outputDir, goodRawFile)
        outputAnalysisDfToCsv(dfFluorTotal, seqs, segments, outputDir, totalRawFile)
        # add to dataframe that will be used to analyze fluorescence
        fluorGoodCol = dfFluorGood['Fluorescence']
        dfAvgGood.insert(i-1, replicate+'-Fluor', fluorGoodCol)
        fluorTotalCol = dfFluorTotal['Fluorescence']
        dfAvgTotal.insert(i-1, replicate+'-Fluor', fluorTotalCol)
        i+=1
    # get average, stdev, etc. from reconstructed fluorescence
    dfAvgGood = getReconstructedFluorescenceStats(dfAvgGood)
    dfAvgTotal = getReconstructedFluorescenceStats(dfAvgTotal)
    return dfAvgGood, dfAvgTotal

# TODO: add in all of the math parts as descriptions below
# sequence proportion:
# 
def calcSeqProportionInBin(sequence, totalSeqCount, binName, dfRep, dfFlow):
    # get sequence count in bin
    seqCount = dfRep.loc[sequence][binName]
    # get percent population in bin
    percent = dfFlow.loc['Percent'][binName]
    # calculate the sequence proportion for a single bin
    prop = percent*seqCount/totalSeqCount
    return prop

# loop through all sequences and calculate the sequence proportion (numerator):
# 
def calculateNumerators(seqs, inputFile, binName, dfRep, dfFlow, usePercents):
    # get total counts of all sequences in bin
    #TODO: fix this so the header is the names
    dfCount = pd.read_csv(inputFile, delimiter='\t', header=None, skiprows=range(0,3), nrows=1)
    goodNumerators = []
    allNumerators = []
    if usePercents is False: 
        goodSeqCount = dfCount.iloc[:,4][0]
        totalAllSeqCount = dfCount.iloc[:,0][0]
        for seq in seqs:
            goodNumerator = calcSeqProportionInBin(seq, goodSeqCount, binName, dfRep, dfFlow)
            totalNumerator = calcSeqProportionInBin(seq, totalAllSeqCount, binName, dfRep, dfFlow)
            goodNumerators.append(goodNumerator)
            allNumerators.append(totalNumerator)
    else:
        # set binPercent as 1 so equation just multiplies the percent found in a bin times percent of sequence in bin
        goodBinPercent = 1
        # set binPercent to the total percent: divide the good bin percent by total to get percent of sequence in bin
        # against all sequences in the population (both good and bad counted)
        totalBinPercent = goodBinPercent/dfCount.iloc[:,5][0]
        for seq in seqs:
            goodNumerator = calcSeqProportionInBin(seq, goodBinPercent, binName, dfRep, dfFlow)
            totalNumerator = calcSeqProportionInBin(seq, totalBinPercent, binName, dfRep, dfFlow)
            goodNumerators.append(goodNumerator)
            allNumerators.append(totalNumerator)
    return goodNumerators, allNumerators
    

# calculate the denominator for reconstructed fluorescence calculation
def calculateDenominatorsForSequence(seqCount, totalSeqCount, currBin, dfFlow):
    # get percent population in bin
    percent = dfFlow.loc['Percent'][currBin]
    # calculate the denominator for a single bin
    seqDenom = percent*seqCount/totalSeqCount
    return seqDenom

# get the counts that can be used for good seqs and total seqs:
# 
def getGoodSeqAndTotalSeqCounts(inputDir, currBin):
    inputFile = inputDir + currBin+'.txt'
    dfCount = pd.read_csv(inputFile, delimiter='\t', header=None, skiprows=range(0,3), nrows=1)
    goodSeqCount = dfCount.iloc[:,4][0]
    totalAllSeqCount = dfCount.iloc[:,0][0]
    return goodSeqCount, totalAllSeqCount

# loops through all sequences and all bins for that sequence and calculates the reconstructed fluorescence denominator
# f*seqCount/binCount
def calculateDenominators(seqs, inputDir, bins, dfRep, dfFlow, usePercents):
    goodSeqDenoms = []
    allSeqDenoms = []
    # loop through all sequences to calculate a denominator for each
    for seq in seqs:
        # denominator variable to hold for each sequence
        sumDenomGood = 0
        sumDenomAll = 0
        for currBin in bins:
            if usePercents is False:
                # get total counts of all sequences in bin
                goodSeqCount, totalSeqCount = getGoodSeqAndTotalSeqCounts(inputDir, currBin)
                # get sequence count in bin
                seqCount = dfRep.loc[seq][currBin]
                # calculate the denominator for the sequence
                goodSeqDenominator = calculateDenominatorsForSequence(seqCount, goodSeqCount, currBin, dfFlow)
                totalSeqDenominator = calculateDenominatorsForSequence(seqCount, totalSeqCount, currBin, dfFlow)
                # add to previous bin denominator total until calculated for all bins
                sumDenomGood += goodSeqDenominator
                sumDenomAll += totalSeqDenominator
            else:
                # get sequence count in bin
                seqPercent = dfRep.loc[seq][currBin]
                goodSeqPercent = 1
                inputFile = inputDir + currBin+'.txt'
                dfPercent = pd.read_csv(inputFile, delimiter='\t', header=None, skiprows=range(0,3), nrows=1)
                totalBinPercent = dfPercent.iloc[:,5][0]
                totalSeqPercent = goodSeqPercent/totalBinPercent
                # calculate the denominator for the sequence
                goodSeqDenominator = calculateDenominatorsForSequence(seqPercent, goodSeqPercent, currBin, dfFlow)
                totalSeqDenominator = calculateDenominatorsForSequence(seqPercent, totalSeqPercent, currBin, dfFlow)
                sumDenomGood += goodSeqDenominator
                sumDenomAll += totalSeqDenominator
        # append the calculated denominator to the allDenominator list
        goodSeqDenoms.append(sumDenomGood)
        allSeqDenoms.append(sumDenomAll)
    return goodSeqDenoms, allSeqDenoms

# calculate the numerator and denominators for each bin
def calculateNumeratorsAndDenominators(seqs, inputDir, bins, dfRep, dfFlow, usePercents=False):
    dfGood = pd.DataFrame()
    dfTotal = pd.DataFrame()
    # calculate the numerators
    for currBin in bins:
        inputFile = inputDir + currBin+'.txt'
        goodNumerators, totalNumerators = calculateNumerators(seqs, inputFile, currBin, dfRep, dfFlow, usePercents)
        colName = currBin+'-Numerator'
        numColumns = len(dfGood.columns)
        dfGood.insert(numColumns, colName, goodNumerators)
        dfTotal.insert(numColumns, colName, totalNumerators)
    # get the denominator for the equation 
    goodSeqDenominators, allSeqDenominators = calculateDenominators(seqs, inputDir, bins, dfRep, dfFlow, usePercents)
    # I think I'm going to make this a new dataframe and print it out (with numerators, denominators, etc.)
    # add denominator to dataframe as a column under title Denominator
    dfGood = dfGood.assign(Denominator = goodSeqDenominators)
    dfTotal = dfTotal.assign(Denominator = allSeqDenominators)
    return dfGood, dfTotal

# calculate the normalized sequence contribution
def calculateNormalizedSequenceContribution(bins, dfGood, dfTotal):
    dfNormGood = pd.DataFrame()
    dfNormTotal = pd.DataFrame()
    for colName, binName in zip(dfGood.columns, bins):
        if 'Denominator' not in colName:
            dfNormGood[binName] = (dfGood[colName]/dfGood['Denominator'])
            dfNormTotal[binName] = (dfTotal[colName]/dfTotal['Denominator'])
    return dfNormGood, dfNormTotal
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
def getReconstructedFluorescenceStats(df):
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
# CALCULATE PERCENT DIFFERENCE
# main function for getting the percent difference between LB and M9 for maltose test
def getPercentDifference(list_df, list_of_hours, numReplicates, seqs, segments, inputDir, outputDir):
    df_percentDiff = pd.DataFrame()
    if len(os.listdir(outputDir)) == 0:
        # list to hold the output df: the first output is for LB and the second is for M9
        # after the loop, it uses both to calculate the percent difference 
        outputDfs = []
        for df, hourList in zip(list_df, list_of_hours):
            outputDf = getMeanPercent(numReplicates, hourList, df, inputDir, outputDir)
            outputDfs.append(outputDf)
        df_percentDiff = calculatePercentDifference(outputDfs[0], outputDfs[1])
        outputDfs.append(df_percentDiff)
        nameList = ['LBPercents.csv', 'M9Percents.csv', 'percentDifference.csv']
        for df, name in zip(outputDfs, nameList):
            outputAnalysisDfToCsv(df, seqs, segments, outputDir, name)
    else:
        print('Percent difference file exists, loading it into dataframe...')
        df_percentDiff = pd.read_csv(outputDir+'percentDifference.csv')
        print('dataframe loaded; If want to remake fluorescence difference file, delete all files in: ', outputDir)
    return df_percentDiff

# get percent change for LB and M9 sequences
def getMeanPercent(numReplicates, listHours, df, inputDir, outputDir):
    # loop through all hours collected during maltose test
    # initialize dataframe to hold the averages for each replicate
    dfAvg = pd.DataFrame()
    for hour in listHours:
        # loop through all replicates for this 
        dfHour = df.filter(like="-"+hour)
        # set all 0 values to NaN
        dfHour = dfHour.replace(0, np.nan)
        # get a dataframe with numerators and denominators
        mean = dfHour.mean(axis=1)
        colLength = len(dfAvg.columns)
        dfAvg.insert(colLength, hour, mean)
    dfAvg = dfAvg.replace(np.nan, 0)
    # add in sequence column to first column, then convert to index
    return dfAvg
            #for seq in seqs:
            #    for colName in colNames:
            #        percent = dfRep.loc[seq][colName]
            #        # TODO: add comparison here

def calculatePercentDifference(dfLB, dfM9):
    # initialize dataframe to hold the percent differences averages
    dfDiff = pd.DataFrame()
    # iterate through columns in LB dataframe
    for col in dfLB.columns:
        LB = dfLB[col]
        M9 = dfM9.iloc[:,0]
        subtract = M9.subtract(LB)
        percentDiff = subtract.divide(LB)*100
        numColumns = len(dfDiff.columns)
        dfDiff.insert(numColumns, col, percentDiff)
    return dfDiff
