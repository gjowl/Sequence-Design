import pandas as pd
import sys
import os
import numpy as np
from functions_v3 import *
import matplotlib.pyplot as plt
import matplotlib.colors

'''
    This file is used to analyze the data from my second set of design runs after CHIP1.
    The goal of this analysis is to determine if this data is better than my previous runs
    by outputting graphs and statistics to a csv file. I can then compare those graphs and
    data to the previous design runs from CHIP1, aiming to have an expectation for the fluorescence
    output depending on the energies, geometry, and sequence of the protein.
'''

def getEnergyDifferenceDf(df_list, columns):
    # loop through each region
    outputDf = pd.DataFrame()
    for df in df_list:
        # get the mean and standard deviation for each column
        tmpDf = getMeanAndSDDf(df, cols)
        # merge the region column
        tmpDf = pd.merge(tmpDf, pd.DataFrame({'Region': [df['Region'].values[0]]}), how='outer', left_index=True, right_index=True)
        # concat the tmpDf to the outputDf
        outputDf = pd.concat([outputDf, tmpDf], axis=0, ignore_index=True)
    return outputDf

# Read in the data from the csv file
df = pd.read_csv(sys.argv[1], sep=',', header=0)
cwd = os.getcwd()
kdeFile = cwd+'/2020_09_23_kdeData.csv'
seqEntropyFile = cwd+'/2021_12_05_seqEntropies.csv'
listAA = ["A", "F", "G", "I", "L", "S", "T", "V", "W", "Y"]

# read in kde data as a dataframe
df_kde = pd.read_csv(kdeFile)

# Set up output directory
outputDir = setupOutputDir(sys.argv[1])

# only keep the unique sequence with best total energy
df = df.sort_values(by=['Total'], ascending=True)
# keep only unique sequences, and the unique sequence with the lowest total energy
df = df.drop_duplicates(subset=['Sequence'], keep='first')

# loop through dataframe rows and break down into regions
for index, row in df.iterrows():
    # check the xShift value
    if row['startXShift'] <= 7.5:
        # add region column GAS
        df.loc[index, 'Region'] = 'GAS'
    elif row['startXShift'] > 7.5 and row['startCrossingAngle'] < 0:
        # add region column GAS
        df.loc[index, 'Region'] = 'Right'
    elif row['startXShift'] > 7.5 and row['startCrossingAngle'] > 0:
        # add region column Left
        df.loc[index, 'Region'] = 'Left'

# sort by total energy
df = df.sort_values(by=['Total'])
df = getRepackEnergies(df)
df = getGeomChanges(df)
df.to_csv(outputDir+'/allData.csv')

# trim the data
df = df[df['Total'] < -10]
df = df[df['Total'] < df['TotalPreBBOptimize']]

# divide data into dataframes for each region
df_GAS = df[df['Region'] == 'GAS']
df_Left = df[df['Region'] == 'Left']
df_Right = df[df['Region'] == 'Right']

# add region dataframes to a list
df_list = [df_GAS, df_Left, df_Right]
geomList = ['xShift', 'crossingAngle', 'axialRotationPrime', 'zShiftPrime']
df_list = addGeometricDistanceToDataframe(df_list, outputDir, geomList)

# loop through each region
df_avg = pd.DataFrame()
for df in df_list:
    region = df['Region'].values[0]
    # add region column to start of df
    dir = outputDir + '/' + region
    # make a directory for each region
    if not os.path.exists(dir):
        os.makedirs(dir)
    # get the top 100 sequences in Total Energy for each region
    tmpDf = df[df['geometryNumber'] > 0]
    # remove sequences where repack energy is greater than 0
    tmpDf = tmpDf[tmpDf['RepackChange'] < 0]
    # rid of anything with geometric distance > 0.5
    tmpDf = tmpDf[tmpDf['GeometricDistance'] < 1]
    # loop through each geometryNumber
    outputFile = dir + '/repackEnergyAnalysis.png'
    plotMeanAndSDBarGraph(tmpDf, outputFile, 'geometryNumber', 'RepackChange')
    outputFile = dir + '/SASADiff.png'
    plotMeanAndSDBarGraph(tmpDf, outputFile, 'geometryNumber', 'SASADiff')
    
    # set the below up to look at just the regions, not the whole geom
    plotGeomKde(df_kde, tmpDf, 'Total', dir, 'startXShift', 'startCrossingAngle')
    bestDf = tmpDf.head(50)
    bestDf.to_csv(outputDir+'/top50_'+bestDf['Region'].iloc[0]+'.csv')

cols = ['VDWDiff', 'HBONDDiff', 'IMM1Diff', 'Total', 'GeometricDistance']
df_avg = getEnergyDifferenceDf(df_list, cols)

plotEnergyDiffs(df_avg, outputDir)
getAAPercentageComposition(df_list, seqEntropyFile, listAA, 'InterfaceSequence', outputDir)

"""
    - compare geometries from duplicate sequences
    - compare geometries from non-duplicate sequences (kde plots for this and above?)\
    - scatterplots of predicted fluorescence...?
    - overlay of kde plots for CHIP1 vs now; maybe overlay of geometries that worked in CHIP1
    - bar graph of each of the terms with mean total energy for the top 100 sequences for each region
"""
