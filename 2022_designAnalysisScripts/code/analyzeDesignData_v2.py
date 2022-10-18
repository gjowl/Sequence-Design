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

def getRepackEnergies(df):
    # add in dimer vs monomer energy difference
    df['VDWDiff'] = df['VDWDimerBBOptimize'] - df['VDWMonomer']
    df['HBONDDiff'] = df['HBONDDimerBBOptimize'] - df['HBONDMonomer']
    df['IMM1Diff'] = df['IMM1DimerBBOptimize'] - df['IMM1Monomer']
    df['VDWRepackDiff'] = df['VDWDimerBBOptimize'] - df['VDWDimerPreBBOptimize']
    df['HBONDRepackDiff'] = df['HBONDDimerBBOptimize'] - df['HBONDDimerPreBBOptimize']
    df['IMM1RepackDiff'] = df['IMM1DimerBBOptimize'] - df['IMM1DimerPreBBOptimize']
    df['RepackChange'] = df['Total'] - df['TotalPreBBOptimize']
    return df

def plotMeanAndSDBarGraph(df, xAxis, yAxis):
    df_avg = df.groupby(xAxis)[yAxis].mean().reset_index()
    # plot the mean and standard deviation of the repack change for each geometry number on a bar graph using matplotlib
    fig, ax = plt.subplots()
    ax.bar(df_avg[xAxis], df_avg[yAxis], yerr=df.groupby(xAxis)[yAxis].std().reset_index()[yAxis])
    ax.set_xlabel(xAxis)
    ax.set_ylabel(yAxis)
    ax.set_title('Average '+yAxis+' for '+xAxis)
    # set x axis to be integers
    ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
    plt.savefig(outputDir+'/avgRepackChange.png')
    plt.close()

def plotEnergyDiffs(df, outputDir, region):
    # data columns to plot
    n = len(df)
    x = np.arange(n)*3
    width = 1
    # get the VDW energy difference column
    VDWDiff = df['VDWDiff']
    # get the HBOND energy difference column
    HBONDDiff = df['HBONDDiff']
    # get the IMM1 energy difference column
    IMM1Diff = df['IMM1Diff']
    # setup the bar plots for each energy difference
    fig, ax = plt.subplots()
    # plot the VDW energy difference with standard deviation
    #ax.bar(x, VDWDiff, width, color='cornflowerblue', edgecolor='black', yerr=df['sdVDW'], label='VDW')
    #ax.bar(x, VDWDiff, width, yerr=df['VDWRepackDiff'].std(), label='VDW')
    p1 = plt.bar(x-0.5, VDWDiff, width, yerr=df['sdVDW'], color='cornflowerblue', edgecolor='black')
    # plot the HBOND energy difference adjacent to the VDW energy difference
    p2 = plt.bar(x+0.5, HBONDDiff, width, yerr=df['sdHBOND'], color='lightcoral', edgecolor='black')
    p3 = plt.bar(x+1.5, IMM1Diff, width, yerr=df['sdIMM1'],color='g', edgecolor='black')
    # change the dpi to make the image smaller
    fig.set_dpi(2000)
    plt.ylabel('Energy')
    plt.title(region+' Energy Plot')
    #plt.ylim(-90,-35)
    #plt.yticks(np.arange(-90, -30, 10))
    plt.legend((p1[0], p2[0], p3[0]), ('VDW', 'HBOND', 'IMM1'))
    # save the number of designs on the plot
    # output the number of sequences in the dataset onto plot top left corner
    #plt.text(0.2, -33, 'N = '+str(n))
    # save plot
    # set empty x axis labels
    plt.xticks(x, [])
    fig.savefig(outputDir+'/energyDiffPlot.png')

# Read in the data from the csv file
df = pd.read_csv(sys.argv[1], sep='\t', header=0)
kdeFile = os.getcwd()+'/' + '2020_09_23_kdeData.csv'

# read in kde data as a dataframe
df_kde = pd.read_csv(kdeFile)

# Set up output directory
outputDir = setupOutputDir(sys.argv[1])

# sort by total energy
df = df.sort_values(by=['Total'])
df.to_csv(outputDir+'/allData.csv')

# rid of anything with Total > 0 and repack energy > 0
df = df[df['Total'] < -10]
df = df[df['VDWDimer'] < 0]

# get the top 100 sequences in Total Energy for each region
df_top = df.nsmallest(100, 'Total')
df = getRepackEnergies(df_top)

# get average VDWDiff, HBONDDiff, and IMM1Diff from the top 100 sequences
avgVDWDiff, sdVDW = df['VDWDiff'].mean(), df['VDWDiff'].std()
avgHBONDDiff, sdHBOND = df['HBONDDiff'].mean(), df['HBONDDiff'].std()
avgIMM1Diff, sdIMM1 = df['IMM1Diff'].mean(), df['IMM1Diff'].std()

# add the average VDWDiff, HBONDDiff, and IMM1Diff to a new dataframe
df_avg = pd.DataFrame({'VDWDiff':[avgVDWDiff], 'HBONDDiff':[avgHBONDDiff], 'IMM1Diff':[avgIMM1Diff], 'sdVDW':[sdVDW], 'sdHBOND':[sdHBOND], 'sdIMM1':[sdIMM1]})

plotMeanAndSDBarGraph(df, 'geometryNumber', 'VDWDiff')
plotEnergyDiffs(df_avg, outputDir, "Right")

# output the top 100 sequences to a csv file
df_top.to_csv(outputDir+'/top100.csv')

# analysis of the top 100 sequences
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

# ideas for analysis
"""
    - compare geometries from duplicate sequences
    - compare geometries from non-duplicate sequences (kde plots for this and above?)\
    - scatterplots of predicted fluorescence...?
    - overlay of kde plots for CHIP1 vs now; maybe overlay of geometries that worked in CHIP1
    - bar graph of each of the terms with mean total energy for the top 100 sequences for each region
"""
