# -*- coding: utf-8 -*-
# @Author: Gilbert Loiseau
# @Date:   2021-12-25
# @Last Modified by:   Gilbert Loiseau
# @Last Modified time: 2022-04-22 15:38:28

"""
This file is used to analyze the data from my sequence designs. It will read in a compiled energy file
and analyze the designs, outputting a summary file for the design run. The hard coded parameters here
are used for my design run that was used to order my first CHIP. It outputs a submit file with sequences
chosen by the given parameters for backboneOptimization and mutations. That data is analyzed by
optimizedBackboneAnalysis.py and the sequences are converted to DNA format for the CHIP using prepareCHIP.py.
"""

from datetime import date
from scipy import stats
from matplotlib import gridspec
import os
import sys
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from analyzerFunctions import *
import helper
from utilityFunctions import *

today = date.today()
today = today.strftime("%Y_%m_%d")

##############################################
#               OUTPUT SETUP
##############################################
# Use the utilityFunctions function to get the name of this program
programName = getProgramName(sys.argv[0])
configFile = sys.argv[1]

# Read in configuration file:
globalConfig = helper.read_config(configFile)
config = globalConfig[programName]

# Config file options:
outputDir               = config["outputDir"]
plotOutputDir           = config["plotOutputDir"]
inputFile               = config["dataFile"]
outFile                 = config["outFile"]
kdeFile                 = config["kdeFile"]
energyLimit             = float(config["energyLimit"])
densityLimit            = float(config["densityLimit"])
crossingAngleLimit      = float(config["crossingAngleLimit"])
sequenceProbabilityFile = config["sequenceProbabilityFile"]
variableFile            = config["variableFile"]
listAA                  = config["listAA"]

#Split the list string into a list of values
listAA = listAA.split(',')

# Setup the output writer for converting dataframes into a spreadsheet
writer = pd.ExcelWriter(outFile)

#TODO: add in all the config options for this shit geez it's a lot ...
# make a directory to output plots
makeOutputDir(plotOutputDir)

# Imports the input csv file into a dataframe
df = pd.read_csv(inputFile, sep=",")
print(df)
dfAll = df

# Gets rid of the original design sequences before the montecarlo walk through sequence space
#   I chose to rid of these sequences because although my design code with the baseline does get a good starting sequence,
#   it doesn't comply well with the membrane AA distribution. I think this is likely because when I was making my baselines,
#   I made it so that they calculated for a random distribution. So whenever these starting sequences is made up of many
#   of one AA, such as Thr (ex. LLLTTTTTATTLTTTLLLL), the baseline favors these interactions enough to choose it as the most
#   stable combination after self consistent mean field. The distributions after including my sequence entropy term are better,
#   but I wanted to have these sequences just in case I ever wanted to look back at them to try to improve my algorithm
df = df[df["SequenceNumber"] > 0]
getAADistribution(df, listAA, outputDir, "AADistribution_All")

dfKde = pd.read_csv(kdeFile)

#########################################################################
#                  SETUP DATAFRAME FOR ANALYSIS
#########################################################################
convertInterfaceToX(df)
addBinNumberColumn(df, -30, 5, 6)
writeDataframeToSpreadsheet(df, writer, "All Data")

#########################################################################
#                  SETUP DATAFRAME FOR ANALYSIS
#########################################################################
df_dup = dfAll[dfAll.duplicated(['Sequence'], keep=False)]
df_dupEnerLimit = df_dup[df_dup['Total'] < energyLimit]
df_dupDensityLimit = df_dupEnerLimit[df_dupEnerLimit['Total'] < densityLimit]

#########################################################################
#     TRIM THE SEQUENCES WITH HIGH ENERGY SCORES AND WITH DUPLICATES
#########################################################################
#TODO: should I just make this a loop? Like have the order of these, run through them, and then it's just a couple lines instead?
# Get dataframe with designs less than the given energy limit
dfEnerLimit = getTrimmedDataframe(df,"Total",energyLimit,True)
writeDataframeToSpreadsheet(dfEnerLimit, writer, "Total Energy < " + str(energyLimit))
#plotDifferenceKde(dfKde, df, "xShift", "crossingAngle", "test", "allTest", outputDir)

# Get dataframe with designs that have the same or less hydrogen bonding in the dimer than the monomer
dfHbondLimit = getTrimmedDataframe(dfEnerLimit,"HBONDDiff",0,False)
writeDataframeToSpreadsheet(dfHbondLimit, writer, "HbondDifference > 0")

# Get dataframe with designs that have density scores within the density limit (high density areas in blue on the kde plot)
dfDensityLimit = getTrimmedDataframe(dfHbondLimit,"angleDistDensity",densityLimit,True)
writeDataframeToSpreadsheet(dfDensityLimit, writer, "Density Group Limit < " + str(densityLimit))

# Get dataframe with designs that have a crossingAngle of higher than -70
# -70 chosen arbitrarily to rid of sequences that likely would not be stable due to membrane entropy
dfAngleLimit = getTrimmedDataframe(dfDensityLimit,"crossingAngle",crossingAngleLimit,False)
writeDataframeToSpreadsheet(dfAngleLimit, writer, "Angle Limit > " + str(crossingAngleLimit))

##################################################################################
#     CALCULATE MEMBRANE PROTEIN SEQUENCE VS INTERFACE SEQUENCE PROBABILITY
##################################################################################
# Create Sequence Probability dictionary from input file
dfSeqProb = pd.read_csv(sequenceProbabilityFile, sep=",")

##############################################
#         ANALYZE THE DATA
##############################################
# Get columns to analyze (all numeric columns)
df_noDup = dfAngleLimit.drop_duplicates(subset=['Sequence'], keep=False)
noDuplicateSeqTotal = getNumberOfSequences(df_noDup)
geoms = getNumberOfGeometries(df_noDup)
print("No Duplicates: " + str(noDuplicateSeqTotal) + "; " + str(geoms))
writeDataframeToSpreadsheet(df_noDup, writer, "No Duplicate Sequences")

getAADistribution(df_noDup, listAA, outputDir, "AADistribution_Trimmed")
# Output general analysis file, taking averages for all of the columns that are numeric
numberOfBins = 9
columnNames = ["Total", "VDWDiff", "HBONDDiff", "IMM1Diff", "xShift", "crossingAngle", "axialRotation", "zShift"]
sheetNames = ["Final Data Bin Summary"]
#analyzeDataframe(dfInterfaceLimit, numberOfBins, "Total", columnNames, sheetNames, writer)

filenames = ['All Data', 'Energy Limit', 'Hbond Limit', 'Density Limit', 'Angle Limit', 'No Duplicates', 'Duplicates', 'Duplicate Energy Limit', 'Duplicate Density Limit']
dfNames = ['All Data', 'Total Energy < '+str(energyLimit), 'Hbond Limit',  'Density Limit', 'Angle Limit > -70', 'No Duplicates', 'Duplicates', 'Duplicate Energy < '+str(energyLimit), 'Duplicate Density < 8']
listDf = [dfAll, dfEnerLimit, dfHbondLimit, dfDensityLimit, dfAngleLimit, df_noDup, df_dup, df_dupEnerLimit, df_dupDensityLimit]
colorList = ['purple', 'green', 'blue', 'gray', 'yellow', 'red', 'black', 'black', 'black', 'black', 'black']
outputDataframeComparison(listDf, dfNames, outputDir)

#TODO: add in options to run these or not; make this runnable by an executable file with options
## Analyze interfacial data:  TODO: group these two together
interfaceAnalyzer(df, columnNames, outputDir, writer)
interfaceSequenceCounts(df, dfSeqProb, columnNames, outputDir, writer)
#binAndAverageInterfaces(dfInterfaceLimit, numberOfBins, outputDir)

# Plot histograms for list of df with different colors
binList = [-40, -35, -30, -25, -20, -15, -10, -5, 0]
plotKdeOverlayForDfList(dfKde, listDf, dfNames, filenames, 'Distance', 'Angle', plotOutputDir)
plotHistogramsForDfList(listDf, binList, colorList, dfNames, filenames, "Total", plotOutputDir)
#plotHistogramsForDfList(listDf, colorList, dfNames, filenames, "VDWDiff", plotOutputDir)
#plotHistogramsForDfList(listDf, colorList, dfNames, filenames, "Total", plotOutputDir)

energySortedDf = df_noDup.sort_values(by='Total', ascending=True)
print(energySortedDf)
writeConfigurationFile(energySortedDf, variableFile)

writer.save()
writer.close()
