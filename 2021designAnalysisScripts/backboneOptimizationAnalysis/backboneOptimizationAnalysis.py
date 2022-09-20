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
import holder
from utilityFunctions import *
from backboneOptimizationAnalysisFunctions import *


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

# list to hold made dataframes in for output
dataList = []

# Read in the input csvfile
df = pd.read_csv(inputFile, sep=",")
dataAll = holder.data(df, "All")
dataList.append(dataAll)

# Get list of lists of bins
binList = getBins(df, 'Total', -50, 0, 5)

# extract only the original design sequences
dataDesign = dataAll.compareColumns("Starting Sequence","Sequence","Designs")
dataList.append(dataDesign)

#TODO: write this so that it outputs a dataframe that gets output to the summary file for the last sequence (and maybe each segment)
sequenceNumbersPerBin = numberSequenceInBin(df, binList, -50)
for bin, num in zip(binList, sequenceNumbersPerBin):
    print(bin, ": ", num)
bestDf = df[df['Total'] < -50]

# get a dataframe of duplicate sequences
dataDup = dataAll.getDuplicates("Sequence")
dataList.append(dataDup)

# extract the mutants for each design sequence and remove any of the duplicates
dfMutant = df[df["Starting Sequence"] != df["Sequence"]]
dataMut = holder.data(dfMutant, "Mutant")
dataMut = dataMut.filterDuplicates("Sequence")
dataList.append(dataMut)

# only keeps mutants that have the desired amount of stable and clashing sequences from backbone optimization
# (ex. if stable = 6, mutants with less than 6 stable sequences (total energy < 0) will be removed)
dfMutants = checkForClashAndStable(dfMutant,7,3)

# For the number of desired segments, generate segments and add to CHIP dataframe
dfSegments = getSegments(dfMutants, dfKde, plotOutputDir, redundant, binList, numSequences, totalSegments, seed)
dataSegments = holder.data(dfSegments, "Segments")
dataList.append(dataSegments)

# Add original design sequences to segments and output the number of sequences in each bin for entire CHIP
print(dataSegments.getDf())
dfDesign = dataDesign.getDf()
dfCHIP = getDesignSequencesForSegment(dfDesign, dfSegments)
dfCHIP = pd.concat([dfSegments,dfCHIP])
sequenceNumbersPerBin = numberSequenceInBin(dfCHIP, binList, -40)
for bin, num in zip(binList, sequenceNumbersPerBin):
    print(bin, ": ", num)

# get left handed sequences
dfLeft = dfCHIP[dfCHIP['Total'] < 0]
dfLeft = dfCHIP[dfCHIP['crossingAngle'] > 0]
dfLeft = dfLeft[dfLeft['Total'] < 0]
dataLeft = holder.data(dfLeft, 'leftHandStrong')

# get right handed sequences
dfRight = dfCHIP[dfCHIP['crossingAngle'] < 0]
dfRight = dfRight[dfRight['Total'] < 0]
dfRight = dfRight[dfRight['xShift'] > 7.5]
dataRightNonGAS = holder.data(dfRight, 'rightNonGASRegion')

# get stable and clashing sequences
dfStable = dfCHIP[dfCHIP['Total'] < 0]
dfMutClash = dfCHIP[dfCHIP['Total'] > 0]
dfMutClash = dfCHIP[dfCHIP['Total'] < 100000]
dataStable = holder.data(dfStable, 'StableMutants')
dataMutClash = holder.data(dfMutClash, 'ClashingMutants')

# Plot histogram for just the design data
# Get random mutant sequences to fill segments and output Kde and energy histograms for each segment
binList = [-55, -50, -45, -40, -35, -30, -25, -20, -15, -10, -5, 0]
if redundant is True:
    title = 'Design Energies After Backbone Optimization Redundant'
    # plots scatterplot for a dataframe
    plotScatterplotForDataframe(dfStable, 'SegmentNumber', 'Total', "Stable Energies Spread Per segment redundant", 'StablePerSegmentR', plotOutputDir)
    plotScatterplotForDataframe(dfMutClash, 'SegmentNumber', 'Total', "Clash Energies Spread Per segment redundant", 'ClashPerSegmentR', plotOutputDir)
    # plot histogram for just the design data
    plotHistogramForDataframe(df, "Total", binList, title, plotOutputDir)
else:
    title = 'Design Energies After Backbone Optimization NonRedundant'
    # plots scatterplot for a dataframe
    plotScatterplotForDataframe(dfStable, 'SegmentNumber', 'Total', "Stable Energies Spread Per segment nonredundant", 'StablePerSegmentNR', plotOutputDir)
    plotScatterplotForDataframe(dfMutClash, 'SegmentNumber', 'Total', "Clash Energies Spread Per segment nonredundant", 'ClashPerSegmentNR', plotOutputDir)
    # plot histogram for just the design data
    plotHistogramForDataframe(df, "Total", binList, title, plotOutputDir)

#TODO: why doesn't this add up to the total number of sequences I'm testing?
print("Stable Sequences: " + str(len(dfStable['Sequence'].unique())))
print("Clashing Mutants: " + str(len(dfMutClash['Sequence'].unique())))
writeDataListToSpreadsheet(dataList, outputFile)