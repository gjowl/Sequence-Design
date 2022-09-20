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
# read in kde data as a dataframe
df_kde = pd.read_csv(kdeFile)

# Set up output directory
outputDir = setupOutputDir(sys.argv[1])

# define energyCutOff
energyCutOff = -5

# parse the dataframe for energy cutoff and duplicates
df = parseDf(df, energyCutOff)

# check if VDWDiff column is all zeros(for previous runs, the VDWDiff column is incorrect, so replace)
if df['VDWDiff'].sum() == 0:
    # calculate dimer vs monomer energy difference
    df['VDWDiff'] = df['VDWDimer'] - df['VDWMonomer']
    df['HBONDDiff'] = df['HBONDDimer'] - df['HBONDMonomer']
    df['IMM1Diff'] = df['IMM1Dimer'] - df['IMM1Monomer']

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

analysisDir = outputDir
# loop through the dataframes and filenames
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

# could I do a scatterplot for energies vs geometry?

# ideas for analysis
"""
    - compare geometries from duplicate sequences
    - compare geometries from non-duplicate sequences (kde plots for this and above?)\
    - scatterplots of predicted fluorescence...?
    - overlay of kde plots for CHIP1 vs now; maybe overlay of geometries that worked in CHIP1
"""
