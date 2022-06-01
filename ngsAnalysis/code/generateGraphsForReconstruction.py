import sys
from functions import *

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
columnsToAnalyze = ['Total']

# make the output directory if it doesn't exist
makeOutputDir(outputDir)

# read in input file from command line file options
inputFile = sys.argv[1]
df = pd.read_csv(inputFile)

# get a list of dataframes of all sequences that are from the same design group (runNumber or StartSequence)
list_designDf = []
if 'runNumber' in df.columns:
    for num in df['runNumber']:
        designDf = pd.DataFrame()
        designDf = df[df['runNumber'] == num]
        list_designDf = designDf
else:
    for sequence in df['StartSequence']:
        designDf = pd.DataFrame()
        designDf = df[df['StartSequence'] == sequence]
        list_designDf = designDf

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
    for AA in interface:
        if AA != '-':
            index = interface.index(AA)
            numInterface.append(index)
    if numInterface in list_interface:
        continue
    else:
        list_interface.append(numInterface)

for interface in df['Interface']:
    for numInterface in list_interface:
        for index in numInterface:
            if interface[index] == '-':
                

# TODO: input data here for kde plotting; go through the xShifts and crossingAngles and such here for any
# generated dataframes
