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
# TODO: fix this code so that it's easy to run for just one dataframe or for multiples and any other options (different things to analyze;
# should I try to set up a class to run multiple types of graphing modes? linear, exponential, etc. Or different types of things to analyze?)

#MAIN
# variables: if want to make this more multipurpose, add the below into a config file
outputDir = os.getcwd()+'/'
#outputDir = '/mnt/c/Users/gjowl/github/Sequence-Design/ngsAnalysis/2022-5-13/graphs/'
#outputDir = '/exports/home/gloiseau/github/Sequence-Design/ngsAnalysis/2022-5-13/graphs/'
columnsToAnalyze = ['EnergyScore']
r2Cutoff = 0

# make the output directory if it doesn't exist
makeOutputDir(outputDir)
#outputDir = outputDir+'nonGxxxG_vdwDiff/'
#makeOutputDir(outputDir)

# read in input file from command line file options
inputFile = sys.argv[1]
df = pd.read_csv(inputFile)
df = df[df['StartSequence'] == df['Sequence']]
df = df[df['PercentGpa'] > 50]
#df = df[df['MaltosePercentDiff'] > -95]

# get a list of dataframes of all sequences that are from the same design group (runNumber or StartSequence)
#list_designDf = getListOfDfWithUniqueColumnVal(df, 'runNumber')
xAxis = 'EnergyScore'
yAxis = 'PercentGpa' # Fluorescence
stdDev = 'PercentGpaStdDev'

#title = 'allDesigns'
title = 'gxxxgDesigns_higherThan50PercentGpa'
outFile = outputDir+title
createScatterPlot(df, xAxis, yAxis, stdDev, 0, outFile, title)
exit()

# TODO: add an option here to run or not run the below code
getScatterplotsForDfList(list_designDf, 'runNumber', xAxis, yAxis, stdDev, r2Cutoff, outputDir)
# TODO: add in a way to identify any sequences with the same positions for the interface
# I think take the interface, identify which positions are not dash, add that number to a list
# and if sequences match that list then add to dictionary? OR easier would be to go through all,
# get the sequences that match, output that dataframe, then continue from the first one that doesn't match
# that combo in a list of combos (and then it's probably easier to output all of those as dataframes list 
# rather than just converting dictionaries)
list_sameInterfaceDf = []
list_interface = []
for interface in df['Interface']:
    # identify positions of interface that aren't dash
    numInterface = []
    nInterface = 'x'
    i = 0
    for AA in interface:
        if AA != '-':
            index = interface.index(AA,i)
            #print(interface, AA, index)
            numInterface.append(index)
            nInterface = nInterface+str(index)
        i+=1
    list_interface.append(nInterface) 
df['numInterface'] = list_interface
list_interfaceDf = getListOfDfWithUniqueColumnVal(df, 'numInterface')
getScatterplotsForDfList(list_interfaceDf, 'numInterface', xAxis, yAxis, stdDev, r2Cutoff, outputDir)
interfaceFile = outputDir+'interfaces.csv'
df.to_csv(interfaceFile)

df.loc[df[xAxis] > 0, xAxis] = 0
# sorts the df by Total energy score
df = df.sort_values(by=xAxis)
df = df.reset_index(drop=True)
df_designs = df[df['StartSequence'] == df['Sequence']] 
df_mutants = df[df['StartSequence'] != df['Sequence']] 
df_designMaltose = df_designs[df_designs['MaltosePercentDiff'] > -100]
title = 'maltoseTestDesigns'
outFile = outputDir+'maltoseDesigns.png'
createScatterPlot(df_designMaltose, xAxis, yAxis, stdDev, 0, outFile, title)
#title = 'Designs'
#outFile = outputDir+'designs.png'
#csvFile = outputDir+'maltoseDesigns.csv'
#df_designMaltose.to_csv(csvFile, index=False)
#createScatterPlot(df_designs, xAxis, yAxis, 0, outFile, title)
#title = 'mutants'
#outFile = outputDir+'mutants.png'
#createScatterPlot(df_mutants, xAxis, yAxis, 0, outFile, title)