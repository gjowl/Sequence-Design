import sys
from functions import *
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as cs
import random

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

def createScatterPlot(x, y, labels, color, outFile, title):
    fig, ax = plt.subplots()
    #obtain m (slope) and b(intercept) of linear regression line
    m, b = np.polyfit(x, y, 1)
    #add linear regression line to scatterplot 
    plt.plot(x, m*x+b, label='y={:.2f}x+{:.2f}'.format(m, b))
    
    # set axis title
    ax.set_title(title)

    # set axes labels
    ax.set_xlabel('Energy Score')
    ax.set_ylabel('Fluorescence')
    # get a color map based on the length of the input
    colormap = cm.viridis
    colorlist = [cs.rgb2hex(colormap(i)) for i in np.linspace(0, 0.9, len(labels))]
    for i,c in enumerate(colorlist):
        x1=x[i]
        y1=y[i]
        l=labels[i]
        ax.scatter(x1, y1, label=l, s=50, linewidth=0.1, c=c)
    
    #for n in range(len(labels)):
    #    plt.scatter(xAxis, yAxis, label=labels[n])
    #l = plt.legend(labels, loc=len(labels)) 

    
    l1 = plt.legend(fontsize=9)
    l2 = plt.legend(fontsize=6, loc='center right')
    #plt.gca().add_artist(l)
    #plt.gca().add_artist(l1)
    #plt.gca().add_artist(l2)
    # save image to filename
    fig.savefig(outFile,format='png', dpi=1200)

#MAIN
# variables: if want to make this more multipurpose, add the below into a config file
#outputDir = '/mnt/c/Users/gjowl/github/Sequence-Design/ngsAnalysis/2022-5-13/graphs/'
outputDir = '/exports/home/gloiseau/github/Sequence-Design/ngsAnalysis/2022-5-13/graphs/'
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

for designDf in list_designDf:
    designDf = designDf[designDf['Total'] < 100]
    # sorts the designDf by Total energy score
    designDf = designDf.sort_values(by='Total')
    xAxis = designDf['Total']
    yAxis = designDf['Average'] # Fluorescence
    runNumber = designDf['runNumber'][2]
    graphTitle = 'Design '+str(runNumber)
    graphFile = outputDir+graphTitle+'.png'
    label = designDf['Sequence']
    colors = []
    for j in range(len(xAxis)):
        colors.append("#"+''.join([random.choice('ABCDEF0123456789') for i in range(6)]))
    createScatterPlot(xAxis,yAxis,label,colors,graphFile,graphTitle)
    exit()


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
               continue 

# TODO: input data here for kde plotting; go through the xShifts and crossingAngles and such here for any
# generated dataframes