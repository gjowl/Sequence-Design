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

inputDir = "C:\\Users\\gjowl\\Documents\\Senes Lab\\Design Research\\Sequence Design\\Analysis\\"
inputFile = "C:\\Users\\gjowl\\Documents\\Senes Lab\\Design Research\\Sequence Design\\Analysis\\Design_files\\2021_11_24_rawDesignData.csv"
#inputFile = "C:\\Users\\gjowl\\Documents\\Senes Lab\\Design Research\\Sequence Design\\Analysis\\"+today+"\\"+today+"_rawDesignData.csv"#version for when I get everything working so it all runs at once
outFile = outputDir + '_analyzedDesignData.xlsx'
writer = pd.ExcelWriter(outFile)

# Gets the header line to be used for the analysis
header = pd.read_csv(inputFile, nrows=0).columns.tolist()

# Imports the input csv file into a dataframe
## TODO: for the future, would be nice to have something that determines file type and uses the apprpriate
df = pd.read_csv(inputFile, sep=",")

dfAll = df

# make this a setup dataframe function: sets up the interface and interfaceSeq columns for analysis
# TODO: add in a bin number here too; then transition binAndAverage to use this number to get the bin name
removeInterfaceEnds(df)
convertInterfaceToX(df)
addBinNumberColumn(df, -30, 5, 6)
writeDataframeToSpreadsheet(df, writer, "All Data")

########################################################################
#     TRIM THE SEQUENCES WITH HIGH ENERGY SCORES AND WITH DUPLICATES
#########################################################################
# Rid of sequences with high vdW in monomer than dimer (clashing)
df = df[df["VDWDiff"] < 0]
df = df[df["Total"] < -5]

addBinNumberColumn(df, -30, 5, 6)
print(df["Bin Number"])
# Trim duplicate sequences
df.hist(column="Total", bins=[-40,-35,-30,-25,-20,-15,-10,-5], figsize=(25,25), color="purple")
df.hist(column="InterfaceSequenceProbability", bins=10, figsize=(25,25), color="purple")
df = df.drop_duplicates(subset=['Sequence'], keep=False)
df.hist(column="Total", bins=[-40,-35,-30,-25,-20,-15,-10,-5], figsize=(25,25))
df.hist(column="InterfaceSequenceProbability", bins=10, figsize=(25,25), color="purple")
# Trim sequences with energy greater than -5 (basically monomeric)
dfEnerLimit = df[df["Total"] < -5]
# Trim sequences if monomer hydrogen bonding greater than -5 (lowest GASright dimers around -5)
dfEnerLimit = dfEnerLimit[dfEnerLimit["HBONDDiff"] > -5]
writeDataframeToSpreadsheet(dfEnerLimit, writer, "Total Energy < -5")

numberOfBins = 6
columnNames = ["Total", "VDWDiff", "HBONDDiff", "IMM1Diff",'InterfaceSequenceProbability', "xShift", "crossingAngle", "axialRotation", "zShift"]

# Takes number of bins, column to bin,
sheetNames = ["All Binned Data", "All Left Data", "All Right Data"]
#analyzeDataframe(df, numberOfBins, "Total", columnNames, sheetNames, writer)
sheetNames = ["Energy Limit Binned Data", "Energy Limit Left Data", "Enery Limit Right Data"]
#analyzeDataframe(dfEnerLimit, numberOfBins, "Total", columnNames, sheetNames, writer)

# Trim the space by angle limits
#dfLeftLim = df[df["crossingAngle"] < 60]
dfLeftLim = dfEnerLimit[dfEnerLimit["crossingAngle"] < 60]
dfLeftLim = dfLeftLim[dfLeftLim["crossingAngle"] > 10]
#dfRightLim = df[df["crossingAngle"] > -60]
dfRightLim = dfEnerLimit[dfEnerLimit["crossingAngle"] > -60]
dfRightLim = dfRightLim[dfRightLim["crossingAngle"] < -10]
dfLim = dfRightLim.append(dfLeftLim)

sheetNames = ["Angle Limit Binned Data", "Angle Limit Left Data", "Angle Limit Right Data"]
#analyzeDataframe(dfLim, numberOfBins, "Total", columnNames, sheetNames, writer)

##################################################################################
#     CALCULATE MEMBRANE PROTEIN SEQUENCE VS INTERFACE SEQUENCE PROBABILITY
###################################################################################
# Create Sequence Probability dictionary from input file
sequenceProbabilityFile = inputDir + 'SequenceProbabilityFile.csv'
dfSeqProb = pd.read_csv(sequenceProbabilityFile, sep=",")

#analyzeSequencesWithSameInterface(dfLim, columnNames, writer)
#TODO: add in a way to determine number of left and right handed points for geometry (without double counting)
#outputs unique number of values for each column. Since values can be picked multiple times when choosing geometry,
#number of unique geometries is greatest number of all geometries
#Just realized this also helps me with sequences: There are 10395 unique sequences according to this
#TODO: get the values you want from here and save them into a file instead of taking them from terminal
#df_dup = dfEnerLimit[dfEnerLimit.duplicated(['Sequence'], keep=False)]
#df_unique = dfEnerLimit.drop_duplicates(subset=['Sequence'], keep=False)



##############################################
#         ANALYZE THE DATA
##############################################
# For the non-interfacial analysis first:
# comparison of the breakdown of sequences after all the limits I put on them (might just be fine to list)
# histogram of diversity of the library: how many sequences in each energy region; how do these energies change
#   - would be nice to also have sequence logos for these groups, so come up with a scheme to divide those and make sequence logos
# Sequence logos for all sequences vs positive vs negative
# Overall sequence entropy scores of groupings

# Output general analysis file, taking averages for all of the columns that are numeric
columnsToAnalyze = getNumericColumns(df)
numInterface = 2
dfInterfaceLimit = ridOfSequencesWithLessThanXInterfacials(dfLim, numInterface)
dfInterfaceLimit.to_excel(writer, "Interface Limit")
sheetNames = ["Interface Limit Binned Data", "Interface Limit Left Data", "Interface Limit Right Data"]
#analyzeDataframe(dfInterfaceLimit, numberOfBins, "Total", columnNames, sheetNames, writer)
x = dfInterfaceLimit.loc[:,'xShift']
y = dfInterfaceLimit.loc[:,'crossingAngle']

dfPath = "C:\\Users\\gjowl\\Downloads\\2020_09_23_kdeData.csv"
dfKde = pd.read_csv(dfPath)
#plotKdeOverlay(dfKde, x, y, 'Distance', 'Angle', 1, outputDir)

valsToGet = ['Sequence', 'crossingAngle']
dfNames = ['All Data', 'Total < -5 AND HbondDifference > -5', 'CrossingAngle: -60 to -10 and +10 to +60', 'Interface AAs less than 3 Leu']
listDf = [dfAll, dfEnerLimit, dfLim, dfInterfaceLimit]
#outputDataframeComparison(listDf, dfNames, outputDir)
# Analyze interfacial data:  TODO: group these two together
interfaceAnalyzer(dfInterfaceLimit, columnNames, outputDir, writer)
interfaceSequenceAnalyzer(dfInterfaceLimit, dfSeqProb, columnNames, outputDir, writer)

#binAndAverageInterfaces(dfInterfaceLimit, numberOfBins, outputDir)
# Plot histograms for list of df with different colors
#plotHistogramsForColumns(df, colNames, binNumber, colorList)
energyCol = ["VDWDiff", "HBONDDiff", "IMM1Diff"]
geomCol = ["xShift", "crossingAngle", "axialRotation", "zShift"]
geomDensityCol = ["angleDistDensity", "axialRotationDensity", "zShiftDensity"]

fig, ax = plt.subplots()
plt.rc('font', size=50)
plt.rc('xtick', labelsize=50)
plt.rc('ytick', labelsize=50)
dfAll.hist(column=energyCol, bins=20, figsize=(25,25), color='purple')
#dfEnerLimit.hist(column=energyCol, bins=20, figsize=(25,25), color='purple')
#dfLim.hist(column=energyCol, bins=20, figsize=(25,25))
dfInterfaceLimit.hist(column=energyCol, bins=20, figsize=(25,25), color='red')
dfAll.hist(column=geomCol, bins=10, figsize=(25,25), color='purple')
#dfEnerLimit.hist(column=geomCol, bins=10, figsize=(25,25), color='purple')
#dfLim.hist(column=geomCol, bins=10, figsize=(25,25))
dfInterfaceLimit.hist(column=geomCol, bins=10, figsize=(25,25), color='red')
dfAll.hist(column='angleDistDensity', bins=10, figsize=(25,25), color='purple')
ax.set_xticklabels([1,2,3,4,5,6,7,8,9,10])
plt.title('')
plt.xlabel('Density Group')
plt.ylabel('Number of Sequences')
plt.savefig(outputDir + "AllData_Density_Histogram.png", bbox_inches='tight', dpi=150)
#dfEnerLimit.hist(column=geomDensityCol, bins=10, figsize=(25,25), color='purple')
#dfLim.hist(column=geomDensityCol, bins=10, figsize=(25,25))
dfInterfaceLimit.hist(column='angleDistDensity', bins=10, figsize=(25,25), color='red')
ax.set_xticklabels([1,2,3,4,5,6,7,8,9,10])
plt.title('')
plt.xlabel('Density Group')
plt.ylabel('Number of Sequences')
plt.savefig(outputDir + "TrimmedData_Density_Histogram.png", bbox_inches='tight', dpi=150)
plt.show()

dfAll.hist(column="Total", bins=[-40,-35,-30,-25,-20,-15,-10,-5], figsize=(25,25), color='purple')
#dfLim.hist(column="Total", bins=[-40,-35,-30,-25,-20,-15,-10,-5], figsize=(25,25))
dfInterfaceLimit.hist(column="Total", bins=[-40,-35,-30,-25,-20,-15,-10,-5], figsize=(25,25), color='red')
dfAll.hist(column="InterfaceSequenceProbability", bins=10, figsize=(25,25), color='purple')
#dfLim.hist(column="InterfaceSequenceProbability", bins=10, figsize=(25,25))
dfInterfaceLimit.hist(column="InterfaceSequenceProbability", bins=10, figsize=(25,25), color='red')

writer.save()
writer.close()
print(dfAll['Interface'].nunique())
print(dfInterfaceLimit['Interface'].nunique())
