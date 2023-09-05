import sys
from functions import *
import pandas as pd
from generateScatterplotFunctions import *

"""
Run as:
    python3 generateGraphsForDataframe.py [inputFile]

This code is used to generate graphs for an input dataframe. Since I will likely
want to use this code for multiple purposes, I will start by making it general use,
outputting scatterplots first to an output directory. Then, you can take those
columns and build other things over top of those scatterplots. Eventually, would
be great to add in other types of graphs to graph that can just be input and created.

I will use this to input datafiles generate by other pieces of code that can then be
analyzed.
"""

#MAIN
# variables: if want to make this more multipurpose, add the below into a config file
outputDir = os.getcwd()+'/'
columnsToAnalyze = ['EnergyScore']
r2Cutoff = 0

# read in input file from command line file options
inputFile = sys.argv[1]
df = pd.read_csv(inputFile)
filename = getFilename(inputFile)

# make the output directory for the scatterplots based on the input filename
outputDir = outputDir+filename+'/'
makeOutputDir(outputDir)

# rid of anything with greater than 0 energy score
df = df[df['EnergyScore'] < 0]

# setup the list of columns to analyze
xAxis = 'EnergyScore'
yAxis = 'PercentGpa' # Fluorescence
stdDev = 'PercentGpaStdDev'

# find sequences with the same interface
list_interface = getNumInterface(df)

# add in the interface number to the dataframe
df['numInterface'] = list_interface

# output the file with the interface column
interfaceFile = outputDir+'interfaces.csv'
df.to_csv(interfaceFile)

# define interface output directory
interfaceDir = outputDir+'interfaces/'

# get the sequences that pass maltose test
df_maltose = df[df['MaltosePercentDiff'] > -100]

# analyze a list of dataframes for all individual sequences and interfaces
list_df = [df, df_maltose]
titles = ['allSequences', 'maltoseSequences']
colList = ['runNumber', 'numInterface']
#for data, title in zip(list_df, titles):
#    outDir = outputDir+title+'/'
#    for colName in colList:
#        # get a list of dataframes of all sequences that are from the same design group (runNumber or StartSequence)
#        listDf = getListOfDfWithUniqueColumnVal(data, colName)
#        # TODO: add an option here to run or not run the below code
#        dir = outDir+colName+'/'
#        makeOutputDir(dir)
#        # output scatterplots for df list
#        getScatterplotsForDfList(listDf, colName, xAxis, yAxis, stdDev, r2Cutoff, dir)

# sorts the df by Total energy score
df = df.sort_values(by=xAxis)
df = df.reset_index(drop=True)

# get the design, mutant, and maltose sequences
df_designs = df[df['StartSequence'] == df['Sequence']] 
df_mutants = df[df['StartSequence'] != df['Sequence']] 
df_maltose = df[df['MaltosePercentDiff'] > -95]

# output a scatterplot of all sequences
titles = ['allSequences', 'designSequences', 'maltoseSequences']
dfs = [df, df_designs, df_maltose]
for title, data in zip(titles, dfs):
    outFile = outputDir+title
    df.loc[df[xAxis] > 0, xAxis] = 0
    createScatterPlot(data, xAxis, yAxis, stdDev, 0, outFile, title)