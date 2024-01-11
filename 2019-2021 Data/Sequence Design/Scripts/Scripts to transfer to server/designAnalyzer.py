"""
Created on Friday November 12 2021
@author: Gilbert Loiseau
"""
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
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import re
import seaborn as sns
from designFunctions import *

##############################################
#               OUTPUT SETUP
##############################################
# Variables
today = date.today()
today = today.strftime("%Y_%m_%d")
outputDir = "C:\\Users\\gjowl\\Documents\\Senes Lab\\Design Research\\Sequence Design\\Analysis\\" + today + "\\"
inputDir = "C:\\Users\\gjowl\\Documents\\Senes Lab\\Design Research\\Sequence Design\\Analysis\\"
inputFile = "C:\\Users\\gjowl\\Documents\\Senes Lab\\Design Research\\Sequence Design\\Analysis\\Design_files\\2021_11_10_rawDesignData.csv"
#inputFile = "C:\\Users\\gjowl\\Documents\\Senes Lab\\Design Research\\Sequence Design\\Analysis\\"+today+"\\"+today+"_rawDesignData.csv"#version for when I get everything working so it all runs at once
outFile = outputDir + 'analyzedDesignData.xlsx'
writer = pd.ExcelWriter(outFile)
energyLimit = -5
densityLimit = 0.7
inputFile = "C:\\Users\\gjowl\\Downloads\\3096seqs.csv"

#Main
# if the outputDirectory doesn't exist, make it
if not os.path.isdir(outputDir):
    print('Creating output directory: ' + outputDir + '.')
    os.mkdir(outputDir)
else:
    print('Output Directory: ' + outputDir + ' exists.')

# make another directory to output plots
plotOutputDir = outputDir+"Plots\\"
if not os.path.isdir(plotOutputDir):
    print('Creating output directory: ' + plotOutputDir + '.')
    os.mkdir(plotOutputDir)
else:
    print('Output Directory: ' + plotOutputDir + ' exists.')

# Imports the input csv file into a dataframe
df = pd.read_csv(inputFile, sep=",")
dfAll = df

# make this a setup dataframe function: sets up the interface and interfaceSeq columns for analysis
listAA = ["A", "F", "G", "I", "L", "S", "T", "V", "W", "Y"]

# Gets rid of the original design sequences before the montecarlo walk through sequence space
#   I chose to rid of these sequences because although my design code with the baseline does get a good starting sequence,
#   it doesn't comply well with the membrane AA distribution. I think this is likely because when I was making my baselines,
#   I made it so that they calculated for a random distribution. So whenever these starting sequences is made up of many
#   of one AA, such as Thr (ex. LLLTTTTTATTLTTTLLLL), the baseline favors these interactions enough to choose it as the most
#   stable combination after self consistent mean field. The distributions after including my sequence entropy term are better,
#   but I wanted to have these sequences just in case I ever wanted to look back at them to try to improve my algorithm
df = df[df["DesignNumber"] > 0]
getAADistribution(df, listAA, outputDir, "AADistribution_All")

dfPath = "C:\\Users\\gjowl\\Downloads\\2020_09_23_kdeData.csv"
dfKde = pd.read_csv(dfPath)

#########################################################################
#                  SETUP DATAFRAME FOR ANALYSIS
#########################################################################
#removeInterfaceEnds(df)
convertInterfaceToX(df)
addBinNumberColumn(df, -30, 5, 6)
writeDataframeToSpreadsheet(df, writer, "All Data")

#########################################################################
#                   GET DUPLICATE SEQUENCE DATA
#########################################################################
# Get dataframe with only 1 copy of duplicated sequences
df_dup = dfAll[dfAll.duplicated(['Sequence'], keep=False)]
duplicateSeqTotal = getNumberOfSequences(df_dup)
print("Duplicates: " + str(duplicateSeqTotal))
writeDataframeToSpreadsheet(df_dup, writer, "Duplicate Sequences")

# Get dataframe of duplicates that have energy less than given energy limit
df_dupEnerLimit = df_dup[df_dup["Total"] < energyLimit]
dupEnerLimitSeqTotal = getNumberOfSequences(df_dupEnerLimit)
print("Energy < " + str(energyLimit) + ": " + str(dupEnerLimitSeqTotal))

# Get dataframe
df_dupDensityLimit = df_dupEnerLimit[df_dupEnerLimit['angleDistDensity'] < densityLimit]
dupDensityLimitSeqTotal = getNumberOfSequences(df_dupDensityLimit)
print("Density Group < 8: " + str(dupDensityLimitSeqTotal))

#########################################################################
#     TRIM THE SEQUENCES WITH HIGH ENERGY SCORES AND WITH DUPLICATES
#########################################################################
# Get dataframe with designs less than the given energy limit
dfEnerLimit = df[df["Total"] < energyLimit]
enerLimitSeqTotal = getNumberOfSequences(dfEnerLimit)
geoms = getNumberOfGeometries(dfEnerLimit)
print("Energy < " + str(energyLimit) + ": " + str(enerLimitSeqTotal) + "; " + str(geoms))
writeDataframeToSpreadsheet(dfEnerLimit, writer, "Total Energy < " + str(energyLimit))
#plotDifferenceKde(dfKde, df, "xShift", "crossingAngle", "test", "allTest", outputDir)

# Get dataframe with designs that have the same or less hydrogen bonding in the dimer than the monomer
dfHbondLimit = dfEnerLimit[dfEnerLimit["HBONDDiff"] > 0]
hbondLimitSeqTotal = getNumberOfSequences(dfHbondLimit)
geoms = getNumberOfGeometries(dfHbondLimit)
print("HbondDifference > 0: " + str(hbondLimitSeqTotal) + "; " + str(geoms))
writeDataframeToSpreadsheet(dfHbondLimit, writer, "HbondDifference > 0")

# Get dataframe with designs that have density scores within the density limit (high density areas in blue on the kde plot)
dfDensityLimit = dfHbondLimit[dfHbondLimit['angleDistDensity'] < densityLimit]
densityLimitSeqTotal = getNumberOfSequences(dfDensityLimit)
geoms = getNumberOfGeometries(dfDensityLimit)
print("Density Group < 7: " + str(densityLimitSeqTotal) + "; " + str(geoms))
writeDataframeToSpreadsheet(dfDensityLimit, writer, "Density Group Limit < 7")

# Get dataframe with designs that have a crossingAngle of higher than -70
# -70 chosen arbitrarily to rid of sequences that likely would not be stable due to membrane entropy
dfAngleLimit = dfDensityLimit[dfDensityLimit['crossingAngle'] > -70]
angleLimitTotal = getNumberOfSequences(dfAngleLimit)
print("Angle > -70: " + str(angleLimitTotal))
writeDataframeToSpreadsheet(dfAngleLimit, writer, "Angle Limit > -70")

##################################################################################
#     CALCULATE MEMBRANE PROTEIN SEQUENCE VS INTERFACE SEQUENCE PROBABILITY
##################################################################################
# Create Sequence Probability dictionary from input file
sequenceProbabilityFile = inputDir + 'SequenceProbabilityFile.csv'
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

submitFile = inputDir+'submitFile.condor'
batchName = 'sequenceDesign'
dirToSave = '/data02/gloiseau/Sequence_Design_Project/vdwSequenceDesign/$(batch_name)'
executable = '/exports/home/mslib/trunk_AS/bin/geomRepack'

energySortedDf = df_noDup.sort_values(by='Total', ascending=True)
print(energySortedDf)
writeConfigurationFile(energySortedDf, submitFile, batchName, dirToSave, executable)

writer.save()
writer.close()
