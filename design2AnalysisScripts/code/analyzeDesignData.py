import pandas as pd
import sys
import os
import numpy as np
from plotGeomKde import *
from functions import *
import matplotlib.pyplot as plt


'''
    This file is used to analyze the data from my second set of design runs after CHIP1.
    The goal of this analysis is to determine if this data is better than my previous runs
    by outputting graphs and statistics to a csv file. I can then compare those graphs and
    data to the previous design runs from CHIP1, aiming to have an expectation for the fluorescence
    output depending on the energies, geometry, and sequence of the protein.
'''

# Read in the data from the csv file
df = pd.read_csv(sys.argv[1])
kdeFile = os.getcwd()+'/' + '2020_09_23_kdeData.csv'

# get directory of the input file
inputDir = os.path.dirname(sys.argv[1])
if inputDir == '':
    inputDir = os.getcwd()

# make output directory
analysisDir = inputDir+'/analyzedData'
# check if the analysis directory exists
if not os.path.exists(analysisDir):
    os.makedirs(analysisDir)

# read in kde data as a dataframe
df_kde = pd.read_csv(kdeFile)

# check if VDWDiff column is all zeros
if df['VDWDiff'].sum() == 0:
    # calculate dimer vs monomer energy difference
    df['VDWDiff'] = df['VDWDimer'] - df['VDWMonomer']
    df['HBONDDiff'] = df['HBONDDimer'] - df['HBONDMonomer']
    df['IMM1Diff'] = df['IMM1Dimer'] - df['IMM1Monomer']

# only keep sequences that where total < 5
df = df[df['Total'] < -5]

# get a dataframe with sequences that are not unique
df_dup = df[df.duplicated(subset=['Sequence'], keep=False)]

# sort the dataframe by sequence and total
df_dup = df_dup.sort_values(by=['Sequence', 'Total'])
df_dup.to_csv(inputDir+"/duplicateSequences.csv", index=False)

# get a dataframe with sequences that are unique
df = df.drop_duplicates(subset=['Sequence'], keep='first')

# sort by total energy
df = df.sort_values(by=['Total'])

# output dfUnique to a csv file
#df_unique.to_csv(cwd+"uniqueSequences.csv", index=False)
df_right, df_left, df_gasright = breakIntoDesignRegions(df)

# get the top 100 sequences in Total Energy for each region
df_rightTop = df_right.nsmallest(100, 'Total')
df_leftTop = df_left.nsmallest(100, 'Total')
df_gasrightTop = df_gasright.nsmallest(100, 'Total')

# add the region data to a list
df_list = [df, df_right, df_left, df_gasright, df_rightTop, df_leftTop, df_gasrightTop]
filename_list = ['All','Right', 'Left', 'GASright', 'RightTop', 'LeftTop', 'GASrightTop']

for df,filename in zip(df_list, filename_list):
    # make output directory
    outputDir = analysisDir+'/'+filename
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)
    plotGeomKde(df_kde, df, 'Total', outputDir)
    plotHist(df, 'Total',outputDir, filename)
    # sort the dataframes by vdwDiff plus hbondDiff using loc
    df = df.sort_values(by=['VDWDiff', 'HBONDDiff'])
    # the below works, but try to think of a better way to plot it to make it more visually appealing and easier to understand
    plotEnergyDiffStackedBarGraph(df,outputDir)
    # sort by total energy
    df = df.sort_values(by=['Total'])
    # output the data to a csv file
    df.to_csv(outputDir+"/data.csv")

# could I do a scatterplot for energies vs geometry
# scatterplot of energies vs geometry
df.plot.scatter(x='crossingAngle', y='Total', c='DarkBlue')
# save scatterplot 
plt.savefig(analysisDir+"/crossAng_scatterplot.png", bbox_inches='tight', dpi=150)

# scatterplot of energies vs geometry
df.plot.scatter(x='xShift', y='Total', c='DarkBlue')
# save scatterplot
plt.savefig(analysisDir+"/xShift_scatterplot.png", bbox_inches='tight', dpi=150)

# ideas for analysis
"""
    - scatterplots for each
    - compare geometries from duplicate sequences
    - compare geometries from non-duplicate sequences (kde plots for this and above?)\
    - look at more structures
    - scatterplots of predicted fluorescence...?
    - overlay of kde plots for CHIP1 vs now; maybe overlay of geometries that worked in CHIP1
"""
