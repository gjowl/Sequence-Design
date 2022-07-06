"""
Created on Friday November 12 2021
@author: Gilbert Loiseau
"""
"""
This file is used to analyze the data from my sequence designs in an automated
way so that I don't have to manually do it every single time after the designs
are finished. It should take and read a file and set up all of the analysis for me.
## TODO: add a better description here
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
import logomaker as lm
from designFunctions import *

##############################################
#               OUTPUT SETUP
##############################################
today = date.today()
today = today.strftime("%Y_%m_%d")
outputDir = "C:\\Users\\gjowl\\Documents\\Senes Lab\\Design Research\\Sequence Design\\Analysis\\" + today + "\\"
if not os.path.isdir(outputDir):
    print('Creating output directory: ' + outputDir + '.')
    os.mkdir(outputDir)
else:
    print('Output Directory: ' + outputDir + ' exists.')

plotOutputDir = outputDir+"Plots\\"
if not os.path.isdir(plotOutputDir):
    print('Creating output directory: ' + plotOutputDir + '.')
    os.mkdir(plotOutputDir)
else:
    print('Output Directory: ' + plotOutputDir + ' exists.')

inputDir = "C:\\Users\\gjowl\\Documents\\Senes Lab\\Design Research\\Sequence Design\\Analysis\\"
inputFile = "C:\\Users\\gjowl\\Documents\\Senes Lab\\Design Research\\Sequence Design\\Analysis\\Design_files\\2021_11_10_rawDesignData.csv"
#inputFile = "C:\\Users\\gjowl\\Documents\\Senes Lab\\Design Research\\Sequence Design\\Analysis\\"+today+"\\"+today+"_rawDesignData.csv"#version for when I get everything working so it all runs at once
outFile = outputDir + 'analyzedDesignData.xlsx'
writer = pd.ExcelWriter(outFile)
inputFile = "C:\\Users\\gjowl\\Downloads\\2678seqs.csv"
# Gets the header line to be used for the analysis
header = pd.read_csv(inputFile, nrows=0).columns.tolist()

# Imports the input csv file into a dataframe
## TODO: for the future, would be nice to have something that determines file type and uses the apprpriate
df = pd.read_csv(inputFile, sep=",")
dfAll = df
energyLimit = 0
# make this a setup dataframe function: sets up the interface and interfaceSeq columns for analysis
# TODO: add in a bin number here too; then transition binAndAverage to use this number to get the bin name
listAA = ["A", "F", "G", "I", "L", "S", "T", "V", "W", "Y"]

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

# Trim duplicate sequences
#df_noDup = df.drop_duplicates(subset=['Sequence'], keep=False)
#noDuplicateSeqTotal = getNumberOfSequences(df)
#print("No Duplicates: " + str(noDuplicateSeqTotal))
#writeDataframeToSpreadsheet(df_noDup, writer, "No Duplicate Sequences")

df_dup = dfAll[dfAll.duplicated(['Sequence'], keep=False)]
duplicateSeqTotal = getNumberOfSequences(df_dup)
print("Duplicates: " + str(duplicateSeqTotal))
writeDataframeToSpreadsheet(df_dup, writer, "Duplicate Sequences")

df_dupEnerLimit = df_dup[df_dup["Total"] < energyLimit]
dupEnerLimitSeqTotal = getNumberOfSequences(df_dupEnerLimit)
print("Energy < " + str(energyLimit) + ": " + str(dupEnerLimitSeqTotal))

df_dupDensityLimit = df_dupEnerLimit[df_dupEnerLimit['angleDistDensity'] < 0.8]
dupDensityLimitSeqTotal = getNumberOfSequences(df_dupDensityLimit)
print("Density Group < 8: " + str(dupDensityLimitSeqTotal))

#########################################################################
#     TRIM THE SEQUENCES WITH HIGH ENERGY SCORES AND WITH DUPLICATES
#########################################################################
# Rid of sequences with high Hbond in monomer than dimer (Hbonding Check)
dfHbondLimit = df[df["HBONDDiff"] > 0]
HbondLimitSeqTotal = getNumberOfSequences(dfHbondLimit)
geoms = getNumberOfGeometries(dfHbondLimit)
print("HBONDDiff < 0: " + str(HbondLimitSeqTotal) + "; " + str(geoms))
writeDataframeToSpreadsheet(dfHbondLimit, writer, "HBONDDiff < 0")

# Rid of sequences with high vdW in monomer than dimer (clashing)
dfVdwLimit = dfHbondLimit[dfHbondLimit["VDWDiff"] < 0]
vdwLimitSeqTotal = getNumberOfSequences(dfVdwLimit)
geoms = getNumberOfGeometries(dfVdwLimit)
print("VDWDiff < 0: " + str(vdwLimitSeqTotal) + "; " + str(geoms))
writeDataframeToSpreadsheet(dfVdwLimit, writer, "VDWDiff < 0")
# Trim sequences with energy greater than -5 (basically monomeric)
# Trim sequences if monomer hydrogen bonding greater than -5 (lowest GASright dimers around -5)
dfEnerLimit = dfVdwLimit[dfVdwLimit["Total"] < energyLimit]
enerLimitSeqTotal = getNumberOfSequences(dfEnerLimit)
geoms = getNumberOfGeometries(dfEnerLimit)
print("Energy < " + str(energyLimit) + ": " + str(enerLimitSeqTotal) + "; " + str(geoms))
writeDataframeToSpreadsheet(dfEnerLimit, writer, "Total Energy < " + str(energyLimit))
#plotDifferenceKde(dfKde, df, "xShift", "crossingAngle", "test", "allTest", outputDir)

dfEner = df[df["Total"] > energyLimit]
enerSeqTotal = getNumberOfSequences(dfEner)
geoms = getNumberOfGeometries(dfEner)
print("Energy > " + str(energyLimit) + ": " + str(enerSeqTotal) + "; " + str(geoms))
writeDataframeToSpreadsheet(dfEner, writer, "Total Energy > " + str(energyLimit))
#writeDataframeToSpreadsheet(dfEnerLimit, writer, "Total Energy < " + str(energyLimit))
#HbondDifference gets rid of no sequences
#dfEnerLimit = dfEnerLimit[dfEnerLimit["HBONDDiff"] > -5]
#enerLimitSeqTotal = getNumberOfSequences(df)
#print("HbondDifference > -5: " + str(enerLimitSeqTotal))
#writeDataframeToSpreadsheet(dfEnerLimit, writer, "Total Energy < " + str(energyLimit))

# Trim the space by angle limits
#dfLeftLim = df[df["crossingAngle"] < 60]
#dfAngleLimit = dfEnerLimit[dfEnerLimit["crossingAngle"] < 60]
#angleLeftLimitSeqTotal = getNumberOfSequences(dfAngleLimit)
#print("Angle < 60: " + str(angleLeftLimitSeqTotal))
#dfAngleLimit = dfAngleLimit[dfAngleLimit["crossingAngle"] > -60]
#angleRightLimitSeqTotal = getNumberOfSequences(dfAngleLimit)
#print("Angle > -60: " + str(angleRightLimitSeqTotal))
#writeDataframeToSpreadsheet(dfAngleLimit, writer, "CrossingAngle Limit")
dfDensityLimit = dfEnerLimit[dfEnerLimit['angleDistDensity'] < 0.8]
densityLimitSeqTotal = getNumberOfSequences(dfDensityLimit)
geoms = getNumberOfGeometries(dfDensityLimit)
print("Density Group < 8: " + str(densityLimitSeqTotal) + "; " + str(geoms))
writeDataframeToSpreadsheet(dfDensityLimit, writer, "Density Group Limit < 8")

# Rid of sequences with high vdW in monomer than dimer (clashing)
#dfVdwLimit = dfHbondLimit[dfHbondLimit["VDWMonomer"] < -25]
#vdwLimitSeqTotal = getNumberOfSequences(dfVdwLimit)
#geoms = getNumberOfGeometries(dfVdwLimit)
#print("VDWDiff < 0: " + str(vdwLimitSeqTotal) + "; " + str(geoms))
#writeDataframeToSpreadsheet(dfVdwLimit, writer, "VDWDiff < 0")
## Trim sequences with energy greater than -5 (basically monomeric)
## Trim sequences if monomer hydrogen bonding greater than -5 (lowest GASright dimers around -5)
#dfEnerLimit = dfVdwLimit[dfVdwLimit["Total"] < 0]
#enerLimitSeqTotal = getNumberOfSequences(dfEnerLimit)
#geoms = getNumberOfGeometries(dfEnerLimit)
#print("Energy < " + str(energyLimit) + ": " + str(enerLimitSeqTotal) + "; " + str(geoms))
#writeDataframeToSpreadsheet(dfEnerLimit, writer, "Total Energy < " + str(-5))
#
#dfDensityLimit = dfEnerLimit[dfEnerLimit['angleDistDensity'] < 0.8]
#densityLimitSeqTotal = getNumberOfSequences(dfDensityLimit)
#geoms = getNumberOfGeometries(dfDensityLimit)
#print("Density Group < 8: " + str(densityLimitSeqTotal) + "; " + str(geoms))
#writeDataframeToSpreadsheet(dfDensityLimit, writer, "Density Group Limit < 8")
#plotDifferenceKde(dfKde, dfEnerLimit, "xShift", "crossingAngle", "test", "allTest", outputDir)
#plotDifferenceKde(dfKde, dfDensityLimit, "xShift", "crossingAngle", "test", "allTest", outputDir)
##################################################################################
#     CALCULATE MEMBRANE PROTEIN SEQUENCE VS INTERFACE SEQUENCE PROBABILITY
###################################################################################
# Create Sequence Probability dictionary from input file
sequenceProbabilityFile = inputDir + 'SequenceProbabilityFile.csv'
dfSeqProb = pd.read_csv(sequenceProbabilityFile, sep=",")

##############################################
#         ANALYZE THE DATA
##############################################
# Get columns to analyze (all numeric columns)
#columnsToAnalyze = getNumericColumns(df)
df_noDup = dfDensityLimit.drop_duplicates(subset=['Sequence'], keep=False)
noDuplicateSeqTotal = getNumberOfSequences(df_noDup)
geoms = getNumberOfGeometries(df_noDup)
print("No Duplicates: " + str(noDuplicateSeqTotal) + "; " + str(geoms))
writeDataframeToSpreadsheet(df_noDup, writer, "No Duplicate Sequences")
# Assign how a limit for how many leucines are allowed in the interface
#numInterface = 3
#dfInterfaceLimit = ridOfSequencesWithLessThanXInterfacials(dfDensityLimit, numInterface)
#interfaceLimitSeqTotal = getNumberOfSequences(dfInterfaceLimit)
#sheetName = "Interface > " + str(numInterface) + " Leucine"
#print(sheetName + ": " + str(interfaceLimitSeqTotal))
#writeDataframeToSpreadsheet(dfInterfaceLimit, writer, sheetName)

getAADistribution(df_noDup, listAA, outputDir, "AADistribution_Trimmed")
# Output general analysis file, taking averages for all of the columns that are numeric
numberOfBins = 9
columnNames = ["Total", "VDWDiff", "HBONDDiff", "IMM1Diff", "xShift", "crossingAngle", "axialRotation", "zShift"]
sheetNames = ["Final Data Bin Summary"]
#analyzeDataframe(dfInterfaceLimit, numberOfBins, "Total", columnNames, sheetNames, writer)
#x = dfInterfaceLimit.loc[:,'xShift']
#y = dfInterfaceLimit.loc[:,'crossingAngle']


#plotKdeOverlay(dfKde, x, y, 'Distance', 'Angle', outputDir)

filenames = ['All Data', 'HbondLimit', 'VDWLimit', 'Energy Limit',  'Density Limit', 'Energies greater than limit', 'No Duplicates', 'Duplicates', 'Duplicate Energy Limit', 'Duplicate Density Limit']
dfNames = ['All Data', 'Hbond Dimer > Hbond Monomer', 'VDW Dimer < VDW Monomer', 'Total Energy < '+str(energyLimit),  'Density Limit', 'Energy > '+str(energyLimit), 'No Duplicates', 'Duplicates', 'Duplicate Energy < '+str(energyLimit), 'Duplicate Density < 8']
#listDf = [dfAll, dfEnerLimit, dfAngleLimit, dfInterfaceLimit]
listDf = [dfAll, dfHbondLimit, dfVdwLimit, dfEnerLimit, dfDensityLimit, dfEner, df_noDup, df_dup, df_dupEnerLimit, df_dupDensityLimit]
colorList = ['purple', 'purple', 'green', 'blue', 'gray', 'yellow', 'red', 'black', 'black', 'black', 'black']
outputDataframeComparison(listDf, dfNames, outputDir)

#TODO: add in options to run these or not; make this runnable by an executable file with options
## Analyze interfacial data:  TODO: group these two together
interfaceAnalyzer(df, columnNames, outputDir, writer)
interfaceSequenceCounts(df, dfSeqProb, columnNames, outputDir, writer)
#binAndAverageInterfaces(dfInterfaceLimit, numberOfBins, outputDir)

# Plot histograms for list of df with different colors
plotKdeOverlayForDfList(dfKde, listDf, dfNames, filenames, 'Distance', 'Angle', plotOutputDir)
plotHistogramsForDfList(listDf, colorList, dfNames, filenames, "angleDistDensity", plotOutputDir)
#plotHistogramsForDfList(listDf, colorList, dfNames, filenames, "VDWDiff", plotOutputDir)
plotHistogramsForDfList(listDf, colorList, dfNames, filenames, "Total", plotOutputDir)

#plotHistogramsForColumns(df, colNames, binNumber, colorList)
#energyCol = ["VDWDiff", "HBONDDiff", "IMM1Diff"]
#geomCol = ["xShift", "crossingAngle", "axialRotation", "zShift"]
#geomDensityCol = ["angleDistDensity", "axialRotationDensity", "zShiftDensity"]
#
##fig, ax = plt.subplots()
#plt.rc('font', size=50)
#plt.rc('xtick', labelsize=50)
#plt.rc('ytick', labelsize=50)
#dfAll.hist(column=energyCol, bins=20, figsize=(25,25), color='purple')
##dfEnerLimit.hist(column=energyCol, bins=20, figsize=(25,25), color='purple')
##dfLim.hist(column=energyCol, bins=20, figsize=(25,25))
#dfInterfaceLimit.hist(column=energyCol, bins=20, figsize=(25,25), color='red')
#dfAll.hist(column=geomCol, bins=10, figsize=(25,25), color='purple')
##dfEnerLimit.hist(column=geomCol, bins=10, figsize=(25,25), color='purple')
##dfLim.hist(column=geomCol, bins=10, figsize=(25,25))
#dfInterfaceLimit.hist(column=geomCol, bins=10, figsize=(25,25), color='red')
#dfAll.hist(column='angleDistDensity', bins=10, figsize=(25,25), color='purple')
##ax.set_xticklabels([1,2,3,4,5,6,7,8,9,10])
#plt.title('')
#plt.xlabel('Density Group')
#plt.ylabel('Number of Sequences')
#plt.savefig(outputDir + "AllData_Density_Histogram.png", bbox_inches='tight', dpi=150)
##dfEnerLimit.hist(column=geomDensityCol, bins=10, figsize=(25,25), color='purple')
##dfLim.hist(column=geomDensityCol, bins=10, figsize=(25,25))
#dfInterfaceLimit.hist(column='angleDistDensity', bins=10, figsize=(25,25), color='red')
##ax.set_xticklabels([1,2,3,4,5,6,7,8,9,10])
#plt.title('')
#plt.xlabel('Density Group')
#plt.ylabel('Number of Sequences')
#plt.savefig(outputDir + "TrimmedData_Density_Histogram.png", bbox_inches='tight', dpi=150)
#plt.show()
#
#dfAll.hist(column="Total", bins=[-40,-35,-30,-25,-20,-15,-10,-5], figsize=(25,25), color='purple')
##dfLim.hist(column="Total", bins=[-40,-35,-30,-25,-20,-15,-10,-5], figsize=(25,25))
#dfInterfaceLimit.hist(column="Total", bins=[-40,-35,-30,-25,-20,-15,-10,-5], figsize=(25,25), color='red')
#dfAll.hist(column="InterfaceSequenceProbability", bins=10, figsize=(25,25), color='purple')
##dfLim.hist(column="InterfaceSequenceProbability", bins=10, figsize=(25,25))
#dfInterfaceLimit.hist(column="InterfaceSequenceProbability", bins=10, figsize=(25,25), color='red')
#
## Extra stuff that I should add in the code eventually as outputs
#print(dfAll['Interface'].nunique())
#print(dfInterfaceLimit['Interface'].nunique())
#
#df_dup = dfAll[dfAll.duplicated(['Sequence'], keep=False)]
#print(df_dup.nunique())
#df_dup.hist(column='angleDistDensity', bins=10, figsize=(25,25), color = 'green')
#plt.title('')
#plt.xlabel('Density Group')
#plt.ylabel('Number of Sequences')
#writeDataframeToSpreadsheet(df_dup, writer, "Duplicated Sequence Data")
#df_dup = df_dup[df_dup['Total'] < -5]
#print(df_dup.nunique())
#df_dup.hist(column='Total', bins=10, figsize=(25,25), color = 'green')
#df_dup.hist(column=geomCol, bins=10, figsize=(25,25), color='green')
#
writer.save()
writer.close()

#TODO: make this binning procedure standardixed so as soon as I change then umber of bins,
#it will auto generate these bins based on binSize
#for i in range(numberOfBins):
#    writer = pd.ExcelWriter(outputDir + "Bin_" + str(i) + "_list.xlsx")
#    tmpDf = dfInterfaceLimit[dfInterfaceLimit["Bin Number"] == i]
#    writeDataframeToSpreadsheet(tmpDf, writer, "Bin_"+str(i))
#    writer.save()
#    writer.close()
