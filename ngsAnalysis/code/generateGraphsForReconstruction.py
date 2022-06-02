import sys
from functions import *
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as cs
import random
import re

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

def outputRegressionLine(x, y):
    #obtain m (slope) and b(intercept) of linear regression line
    m, b = np.polyfit(x, y, 1)
    #add linear regression line to scatterplot 
    line = plt.plot(x, m*x+b, label='y={:.2f}x+{:.2f}'.format(m, b), c='orange')
    return line
    
def createScatterPlotDiffLabels(df, xAxis, yAxis, labelName, outFile, title):
    # setup figure and axes
    fig, ax = plt.subplots()
    # set axis title
    ax.set_title(title)
    # set axes labels
    ax.set_xlabel('Energy Score')
    ax.set_ylabel('Fluorescence')
    # get values from dataframe
    x = df[xAxis]
    y = df[yAxis]

    # values need to be in list format for scatterplot
    xList = x.tolist()
    yList = y.tolist()
    labels = df[labelName].tolist()
    # get a color map based on the length of the input
    colormap = cm.viridis
    colorlist = [cs.rgb2hex(colormap(i)) for i in np.linspace(0, 0.9, len(labels))]
    # loop through the dataframe to output the scatterplot with points in different colors 
    for i,c in enumerate(colorlist):
        x1=xList[i]
        y1=yList[i]
        l=labels[i]
        plt.scatter(x1, y1, label=l, s=50, linewidth=0.1, c=c)
    # TODO: fix so that there's a separate legend for regression
    # outputs a regression line and equation 
    l1 = outputRegressionLine(x, y)
    l2 = plt.legend(fontsize=6, loc='center right')
    #plt.gca().add_artist(l2)
    # save image to filename
    fig.savefig(outFile,format='png', dpi=1200)
    
def createScatterPlot(df, xAxis, yAxis, outFile, title):
    # setup figure and axes
    fig, ax = plt.subplots()
    # set axis title
    ax.set_title(title)
    # set axes labels
    ax.set_xlabel('Energy Score')
    ax.set_ylabel('Fluorescence')
    # get values from dataframe
    x = df[xAxis]
    y = df[yAxis]
    stdDev = df['StdDev']
    # get the wild type value from the dataframe
    df_wt = df[df['StartSequence'] == df['Sequence']] 
    x_wt = df_wt[xAxis]
    y_wt = df_wt[yAxis]
    # values need to be in list format for scatterplot
    xList = x.tolist()
    yList = y.tolist()
    # plot scatter plot for mutants
    plt.errorbar(x, y, stdDev, linestyle='None', marker='', capsize=4, c='black')
    plt.scatter(x, y, s=50, linewidth=0.1)
    plt.scatter(x_wt, y_wt, s=50, linewidth=0.1, c='r')
    # TODO: fix so that there's a separate legend for regression
    # outputs a regression line and equation 
    l1 = outputRegressionLine(x, y)
    l2 = plt.legend(fontsize=6, loc='center right')
    #plt.gca().add_artist(l2)
    # save image to filename
    fig.savefig(outFile,format='png', dpi=1200)
    plt.close()

def getScatterplotsForDfList(list_df, xAxis, yAxis):
    # iterate through the list of dataframes
    for df in list_df:
        # removes anything with an energy score below 100
        df = df[df[xAxis] < 100]
        # sorts the df by Total energy score
        df = df.sort_values(by=xAxis)
        df = df.reset_index(drop=True)
        # get the runNumber for the filename
        runNumber = df['runNumber'][0]
        graphTitle = 'Design '+str(runNumber)
        graphFile = outputDir+graphTitle+'.png'
        # create the scatter plot
        createScatterPlot(df,xAxis,yAxis,graphFile,graphTitle)
        exit()

#MAIN
# variables: if want to make this more multipurpose, add the below into a config file
outputDir = '/mnt/c/Users/gjowl/github/Sequence-Design/ngsAnalysis/2022-5-13/graphs/'
#outputDir = '/exports/home/gloiseau/github/Sequence-Design/ngsAnalysis/2022-5-13/graphs/'
columnsToAnalyze = ['Total']

# make the output directory if it doesn't exist
makeOutputDir(outputDir)

# read in input file from command line file options
inputFile = sys.argv[1]
df = pd.read_csv(inputFile)

# get a list of dataframes of all sequences that are from the same design group (runNumber or StartSequence)
list_designDf = []
if 'runNumber' in df.columns:
    for num in df['runNumber'].unique():
        designDf = pd.DataFrame()
        designDf = df[df['runNumber'] == num]
        list_designDf.append(designDf)
else:
    for sequence in df['StartSequence']:
        designDf = pd.DataFrame()
        designDf = df[df['StartSequence'] == sequence]
        list_designDf.append(designDf)

#TODO: I should convert these in the final alldata dataframe to actual names (energy score and fluorescence)
xAxis = 'Total'
yAxis = 'Average' # Fluorescence

#getScatterplotsForDfList(list_designDf, xAxis, yAxis)

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
interfaceFile = outputDir+'interfaces.csv'
df.to_csv(interfaceFile)
exit()

# TODO: how do I get rid of things that don't seem to correlate...? What is a good way to cutoff data?
# Maybe looking at the counts per LB and M9 for some sequences?
# TODO: look at percent GpA and energy score differences to choose sequences to look at docking and backbone repacks:
# come up with some way to say that these numbers are too different?
# some way to show correlation +/- a value or so? as in like move down 10%: what is the energy score and what's a 
# reasonable acceptable range for that score


for interface in df['Interface']:
    for numInterface in list_interface:
        print(numInterface)
        for index in numInterface:
            if interface[index] == '-':
                print(index)

pattern = '^A....G$'
test_string = 'AGLLAG'
result = re.match(pattern, test_string)
if result:
  print("Search successful.")
else:
  print("Search unsuccessful.")	

pattern = '^a...s$'
test_string = 'abyss'
result = re.match(pattern, test_string)
if result:
  print("Search successful.")
else:
  print("Search unsuccessful.")	

# TODO: input data here for kde plotting; go through the xShifts and crossingAngles and such here for any
# generated dataframes