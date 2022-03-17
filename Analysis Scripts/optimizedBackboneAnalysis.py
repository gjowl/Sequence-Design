# @Author: Gilbert Loiseau
# @Date:   2021-12-21
# @Filename: optimizedBackboneAnalysis2.py
# @Last modified by:   Gilbert Loiseau
# @Last modified time: 2021-12-29

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
from utility import *
from designFunctions import *
from optimizeBackboneFunctions import *
import gc

#TODO: make above into package
"""
This code takes sequences randomly from my optimizedBackbones and mutants to create a flat distribution of sequences to order
"""
# Variables
outputDir = "C:\\Users\\gjowl\\Documents\\Senes Lab\\Design Research\\Sequence Design\\Analysis\\"
outputFile = outputDir + 'optimizedBackboneAnalysis.xlsx'
plotOutputDir = outputDir+"CHIP_Plots\\"
inputFile = "C:\\Users\\gjowl\\Downloads\\allBackboneOptimization.csv"
numSequences = 8
totalSegments = 12
sequencesPerBin = 80
sequencesPerSegment = 500
numRandom = 60
# variables for original kde geometry plot from membranePDBs
dfPath = "C:\\Users\\gjowl\\Downloads\\2020_09_23_kdeData.csv"
dfKde = pd.read_csv(dfPath)

# Main

# If output directory does not exist, create it
if not os.path.isdir(plotOutputDir):
    print('Creating output directory: ' + plotOutputDir + '.')
    os.mkdir(plotOutputDir)
else:
    print('Output Directory: ' + plotOutputDir + ' exists.')

# initialize writer for output file
writer = pd.ExcelWriter(outputFile)

# list to hold made dataframes in for output
dfList = []

#TODO: I still have to fix it so that I can instantly run this code...right now, I have to make a change to the file first
# Read in the input csvfile
df = pd.read_csv(inputFile, sep=",")
writeDataframeToSpreadsheet(df, writer, 'All')

# extract only the original design sequences
dfDesign = df[df["StartSequence"] == df["Sequence"]]
writeDataframeToSpreadsheet(dfDesign, writer, 'Design Sequences')

# Get list of lists of bins
binList = getBins(df, 'Total', -40, 0, 5)

#TODO: write this so that it outputs a dataframe that gets output to the summary file for the last sequence (and maybe each segment)
sequenceNumbersPerBin = numberSequenceInBin(df, binList, -40)
for bin, num in zip(binList, sequenceNumbersPerBin):
    print(bin, ": ", num)
bestDf = df[df['Total'] < -50]
print(len(bestDf['runNumber'].unique()))

#TODO: get a dataframe of the duplicate sequences that are actually chosen for the CHIP
# get a dataframe of duplicate sequences
dfDup = df[df.duplicated(['Sequence'], keep=False)]#These sequences are usually made up of the same backbone geometry (might get rid of any with large differences, but otherwise keep)
writeDataframeToSpreadsheet(dfDup, writer, 'Duplicates')

# extract the mutants for each design sequence and remove any of the duplicates
dfMutant = df[df["StartSequence"] != df["Sequence"]]
dfMutant = dfMutant.drop_duplicates(subset="Sequence", keep=False)

# only keeps mutants that have the desired amount of stable and clashing sequences from backbone optimization
# (ex. if stable = 6, mutants with less than 6 stable sequences (total energy < 0) will be removed)
dfMutants = checkForClashAndStable(dfMutant,5,3)

# Get random mutant sequences to fill segments and output Kde and energy histograms for each segment
dfSegments = pd.DataFrame()
binList1 = [-55, -50, -45, -40, -35, -30, -25, -20, -15, -10, -5, 0]

# For the number of desired segments, generate segments and add to CHIP dataframe
for segNumber in range(1,totalSegments+1):
    if dfSegments.empty is True:
        dfRandomSequences = generateSegment(dfMutants, binList, numSequences, 5, 3)
        dfRandomSequences['SegmentNumber'] = segNumber
        dfSegments = dfSegments.append(dfRandomSequences)
        name = "Segment" + str(num)
    else:
        removePrevSeqList = list(set(dfMutants['runNumber'])-set(dfSegments['runNumber']))
        tmpDf = dfMutants[dfMutants['runNumber'].isin(removePrevSeqList)]
        sequenceNumbersPerBin = numberSequenceInBin(tmpDf, binList, -40)
        #for bin, num in zip(binList, sequenceNumbersPerBin):
        #    print(bin, ": ", num)
        dfRandomSequences = generateSegment(tmpDf, binList, numSequences, 5, 3)
        dfRandomSequences['SegmentNumber'] = segNumber
        dfSegments = dfSegments.append(dfRandomSequences)
        name = "Segment" + str(segNumber)
        #plotHistogramForDataframe(dfRandomSequences, "Total", binList1, name, plotOutputDir)
        plotKdeOverlay(dfKde, dfRandomSequences, 'Distance', 'Angle', plotOutputDir, segNumber)

# Add original design sequences to segments and output the number of sequences in each bin for entire CHIP
dfCHIP = getDesignSequencesForSegment(dfDesign, dfSegments)
dfCHIP = dfSegments.append(dfCHIP)
sequenceNumbersPerBin = numberSequenceInBin(dfCHIP, binList, -40)
for bin, num in zip(binList, sequenceNumbersPerBin):
    print(bin, ": ", num)
writeDataframeToSpreadsheet(dfCHIP, writer, 'Segments')

# Plot histogram for just the design data
filename = 'Design Energies After Backbone Optimization'
listDf = dfDesign
binList = [-55, -50, -45, -40, -35, -30, -25, -20, -15, -10, -5, 0]
plotHistogramForDataframe(df, "Total", binList1, filename, plotOutputDir)

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
plotScatterplotForDataframe(dfStable, 'SegmentNumber', 'Total', "Stable Energies Spread Per segment", 'StablePerSegment', plotOutputDir)
plotScatterplotForDataframe(dfMutClash, 'SegmentNumber', 'Total', "Clash Energies Spread Per segment", 'ClashPerSegment', plotOutputDir)

writeDataframeToSpreadsheet(dfStable, writer, 'StableMutants')
writeDataframeToSpreadsheet(dfMutClash, writer, 'ClashingMutants')
print(len(dfMutClash['Sequence'].unique()))

writer.close()
