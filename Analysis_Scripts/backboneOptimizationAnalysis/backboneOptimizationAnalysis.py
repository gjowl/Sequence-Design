# @Author: Gilbert Loiseau
# @Date:   2021-12-21
# @Filename: optimizedBackboneAnalysis2.py
# @Last modified by:   Gilbert Loiseau
# @Last modified time: 2022-01-07

from datetime import date
import sys
import os
import re
import pandas as pd
import helper
from utilityFunctions import *
from backboneOptimizationAnalysisFunctions import *
import gc

#TODO: make above into package
"""
This code takes sequences randomly from my optimized backbone and mutant data
and selects from a desired subset of sequences to setup a CHIP to order. By
changing the redundant variable to True or False, you will make a library with
redundant or no redundant sequences.
"""
# Use the utilityFunctions function to get the name of this program
programName = getProgramName(sys.argv[0])
configFile = sys.argv[1]

# Read in configuration file:
globalConfig = helper.read_config(configFile)
config = globalConfig[programName]

#Config file variables
outputDir           = config["outputDir"]
outputFile          = config["outFile"]
plotOutputDir       = config["plotDir"]
inputFile           = config["dataFile"]
kdeFile             = config["kdeFile"]
numSequences        = int(config["numSequences"])
totalSegments       = int(config["totalSegments"])
sequencesPerBin     = int(config["sequencesPerBin"])
sequencesPerSegment = int(config["sequencesPerSegment"])
numRandom           = int(config["numRandom"])
redundant           = bool(config["redundant"])
seed                = int(config["seed"])

# variables for original kde geometry plot from membranePDBs
dfKde = pd.read_csv(kdeFile)

# Main
# If output directory does not exist, create it
makeOutputDir(plotOutputDir)

# initialize writer for output file
writer = pd.ExcelWriter(outputFile)

# list to hold made dataframes in for output
dfList = []

#TODO: I still have to fix it so that I can instantly run this code...right now, I have to make a change to the file first
# Read in the input csvfile
df = pd.read_csv(inputFile, sep=",")
writeDataframeToSpreadsheet(df, writer, 'All')

# extract only the original design sequences
dfDesign = df[df["Starting Sequence"] == df["Sequence"]]
writeDataframeToSpreadsheet(dfDesign, writer, 'Design Sequences')

# Get list of lists of bins
binList = getBins(df, 'Total', -50, 0, 5)

#TODO: write this so that it outputs a dataframe that gets output to the summary file for the last sequence (and maybe each segment)
sequenceNumbersPerBin = numberSequenceInBin(df, binList, -50)
for bin, num in zip(binList, sequenceNumbersPerBin):
    print(bin, ": ", num)
bestDf = df[df['Total'] < -50]
print(len(bestDf['runNumber'].unique()))

#TODO: get a dataframe of the duplicate sequences that are actually chosen for the CHIP
# get a dataframe of duplicate sequences
dfDup = df[df.duplicated(['Sequence'], keep=False)]#These sequences are usually made up of the same backbone geometry (might get rid of any with large differences, but otherwise keep)
writeDataframeToSpreadsheet(dfDup, writer, 'Duplicates')

# extract the mutants for each design sequence and remove any of the duplicates
dfMutant = df[df["Starting Sequence"] != df["Sequence"]]
dfMutant = dfMutant.drop_duplicates(subset="Sequence", keep=False)

# only keeps mutants that have the desired amount of stable and clashing sequences from backbone optimization
# (ex. if stable = 6, mutants with less than 6 stable sequences (total energy < 0) will be removed)
dfMutants = checkForClashAndStable(dfMutant,7,3)

# Get random mutant sequences to fill segments and output Kde and energy histograms for each segment
dfSegments = pd.DataFrame()
binList1 = [-55, -50, -45, -40, -35, -30, -25, -20, -15, -10, -5, 0]

# For the number of desired segments, generate segments and add to CHIP dataframe
for segNumber in range(1,totalSegments+1):
    if redundant is True:
        dfRandomSequences = generateSegment(dfMutants, binList, numSequences, 6, 3, seed+segNumber)
        dfRandomSequences['SegmentNumber'] = segNumber
        dfSegments = pd.concat([dfSegments,dfRandomSequences])
        name = "Segment" + str(segNumber)
    else:
        if dfSegments.empty is True:
            dfRandomSequences = generateSegment(dfMutants, binList, numSequences, 6, 3, seed+segNumber)
            dfRandomSequences['SegmentNumber'] = segNumber
            dfSegments = pd.concat([dfSegments,dfRandomSequences])
            name = "Segment" + str(segNumber)
        else:
            removePrevSeqList = list(set(dfMutants['runNumber'])-set(dfSegments['runNumber']))
            tmpDf = dfMutants[dfMutants['runNumber'].isin(removePrevSeqList)]
            sequenceNumbersPerBin = numberSequenceInBin(tmpDf, binList, -40)
            #for bin, num in zip(binList, sequenceNumbersPerBin):
            #    print(bin, ": ", num)
            dfRandomSequences = generateSegment(tmpDf, binList, numSequences, 6, 3, seed+segNumber)
            dfRandomSequences['SegmentNumber'] = segNumber
            dfSegments = pd.concat([dfSegments,dfRandomSequences])
            name = "Segment" + str(segNumber)
            #plotHistogramForDataframe(dfRandomSequences, "Total", binList1, name, plotOutputDir)
            plotKdeOverlay(dfKde, dfRandomSequences, 'Distance', 'Angle', plotOutputDir, segNumber)

# Add original design sequences to segments and output the number of sequences in each bin for entire CHIP
dfCHIP = getDesignSequencesForSegment(dfDesign, dfSegments)
dfCHIP = pd.concat([dfSegments,dfCHIP])
sequenceNumbersPerBin = numberSequenceInBin(dfCHIP, binList, -40)
for bin, num in zip(binList, sequenceNumbersPerBin):
    print(bin, ": ", num)
writeDataframeToSpreadsheet(dfCHIP, writer, 'Segments')

# Plot histogram for just the design data
title = ''
if redundant is True:
    title = 'Design Energies After Backbone Optimization Redundant'
else:
    title = 'Design Energies After Backbone Optimization NonRedundant'

listDf = dfDesign
binList = [-55, -50, -45, -40, -35, -30, -25, -20, -15, -10, -5, 0]
plotHistogramForDataframe(df, "Total", binList1, title, plotOutputDir)

#TODO: Make below into a function that outputs the numbers for certain regions of geometric space
dfMutAngle = dfCHIP[dfCHIP['Total'] < 0]
print(len(dfMutAngle['Sequence'].unique()))

dfMutAngle = dfCHIP[dfCHIP['crossingAngle'] > 0]
dfMutAngle = dfMutAngle[dfMutAngle['Total'] < 0]
writeDataframeToSpreadsheet(dfMutAngle, writer, 'leftHandStrong')
print(len(dfMutAngle['Sequence'].unique()))

dfMutAngle = dfCHIP[dfCHIP['crossingAngle'] < 0]
dfMutAngle = dfMutAngle[dfMutAngle['Total'] < 0]
dfMutAngle = dfMutAngle[dfMutAngle['xShift'] > 7.5]
writeDataframeToSpreadsheet(dfMutAngle, writer, 'rightNonGASRegion')
print(len(dfMutAngle['Sequence'].unique()))

dfStable = dfCHIP[dfCHIP['Total'] < 0]
dfMutClash = dfCHIP[dfCHIP['Total'] > 0]
dfMutClash = dfCHIP[dfCHIP['Total'] < 100000]

# plots scatterplot for a dataframe
if redundant is True:
    plotScatterplotForDataframe(dfStable, 'SegmentNumber', 'Total', "Stable Energies Spread Per segment redundant", 'StablePerSegmentR', plotOutputDir)
    plotScatterplotForDataframe(dfMutClash, 'SegmentNumber', 'Total', "Clash Energies Spread Per segment redundant", 'ClashPerSegmentR', plotOutputDir)
else:
    plotScatterplotForDataframe(dfStable, 'SegmentNumber', 'Total', "Stable Energies Spread Per segment nonredundant", 'StablePerSegmentNR', plotOutputDir)
    plotScatterplotForDataframe(dfMutClash, 'SegmentNumber', 'Total', "Clash Energies Spread Per segment nonredundant", 'ClashPerSegmentNR', plotOutputDir)

writeDataframeToSpreadsheet(dfStable, writer, 'StableMutants')
writeDataframeToSpreadsheet(dfMutClash, writer, 'ClashingMutants')
print(len(dfMutClash['Sequence'].unique()))

writer.close()
