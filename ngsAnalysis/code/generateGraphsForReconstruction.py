import sys
from functions import *
from reconstructionGraphingFunctions import *
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
outputDir = '/mnt/c/Users/gjowl/github/Sequence-Design/ngsAnalysis/2022-5-13/graphs/'
#outputDir = '/exports/home/gloiseau/github/Sequence-Design/ngsAnalysis/2022-5-13/graphs/'
columnsToAnalyze = ['Total']
r2Cutoff = 0

# make the output directory if it doesn't exist
makeOutputDir(outputDir)
outputDir = outputDir+str(r2Cutoff)+'cutoff/'
makeOutputDir(outputDir)

# read in input file from command line file options
inputFile = sys.argv[1]
df = pd.read_csv(inputFile)
df2 = pd.read_csv('/mnt/c/Users/gjowl/github/Sequence-Design/ngsAnalysis/matchingSequences3.csv')

# get dataframe with only non matching sequences from other dataframe
df_nonGxxxg = df[df['Sequence'].isin(df2['Sequence']) == False]
df_nonGxxxg.to_csv(outputDir+'nonGxxxg.csv', index=False)
df = df_nonGxxxg.copy()

# TODO: do this in my actual analysis file
gpaFluor = 109804.5
df['Percent GpA'] = df['Average']/gpaFluor*100
df['StdDev'] = df['StdDev']/gpaFluor*100

# get a list of dataframes of all sequences that are from the same design group (runNumber or StartSequence)
list_designDf = getListOfDfWithUniqueColumnVal(df, 'runNumber')
#TODO: I should convert these in the final alldata dataframe to actual names (energy score and fluorescence)
xAxis = 'Total'
yAxis = 'Percent GpA' # Fluorescence

# replaces all values greater than 0 with 0; this works in the function but not out here?
#df.loc[df[xAxis] > 100, xAxis] = 0

getScatterplotsForDfList(list_designDf, 'runNumber', xAxis, yAxis, r2Cutoff, outputDir)
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
getScatterplotsForDfList(list_interfaceDf, 'numInterface', xAxis, yAxis, r2Cutoff, outputDir)
interfaceFile = outputDir+'interfaces.csv'
df.to_csv(interfaceFile)
exit()

df.loc[df[xAxis] > 0, xAxis] = 0
# sorts the df by Total energy score
df = df.sort_values(by=xAxis)
df = df.reset_index(drop=True)
print(df)
df_designs = df[df['StartSequence'] == df['Sequence']] 
df_mutants = df[df['StartSequence'] != df['Sequence']] 
df_designMaltose = df_designs[df_designs['PercentDiff'] > -100]
print(df_designMaltose)
#title = 'maltoseTestDesigns'
#outFile = outputDir+'maltoseDesigns.png'
#createScatterPlot(df_designMaltose, xAxis, yAxis, 0, outFile, title)
#title = 'Designs'
#outFile = outputDir+'designs.png'
#csvFile = outputDir+'maltoseDesigns.csv'
#df_designMaltose.to_csv(csvFile, index=False)
#createScatterPlot(df_designs, xAxis, yAxis, 0, outFile, title)
title = 'mutants'
outFile = outputDir+'mutants.png'
createScatterPlot(df_mutants, xAxis, yAxis, 0, outFile, title)