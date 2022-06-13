import sys
from functions import *
import matplotlib.pyplot as plt
"""
Run as:
    python3 outputHistogram.py [inputFile]

This code is used to generate a histogram for an input dataframe.
"""

#MAIN
# variables: if want to make this more multipurpose, add the below into a config file
#outputDir = '/mnt/c/Users/gjowl/github/Sequence-Design/ngsAnalysis/2022-5-13/graphs/'
outputDir = '/exports/home/gloiseau/github/Sequence-Design/ngsAnalysis/'
columnsToAnalyze = ['Total']
r2Cutoff = 0.5

# read in input file from command line file options
inputFile = sys.argv[1]
df = pd.read_csv(inputFile)

#yAxis = 'PercentGpa'
#yAxis = 'EnergyScore'
#df.loc[df[yAxis] > 0, yAxis] = 0
#yAxis = 'xShift'
#yAxis = 'crossingAngle'
yAxis = 'axialRotation'
#yAxis = 'zShift'


# read in dataframe and output histogram

df = df.sort_values(by=yAxis)
df = df.reset_index(drop=True)
#df = df[df['MaltosePercentDiff'] > -95]

title = 'No GASright '+yAxis+' histogram'
# setup figure and axes
fig, ax = plt.subplots()
# set axis title
ax.set_title(title)
# set axes labels
ax.set_xlabel(yAxis)
ax.set_ylabel('# Sequences')
# set y-axis limits
#ax.set_ylim(0, 150)
# create histogram of Fluorescence column as y axis and sequence as x axis in dataframe
plt.hist(df[yAxis], color='green', edgecolor='black', linewidth=1.2, rwidth=0.8)
# save figure
fig.savefig(outputDir+'no_GxxxG_histogram_'+yAxis+'.png')