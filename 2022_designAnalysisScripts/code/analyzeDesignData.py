import pandas as pd
import sys
import os
import numpy as np
from analysisFunctions import *
import matplotlib.pyplot as plt
import matplotlib.colors
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D
from functions import *

'''
    This file is used to analyze the data from my second set of design runs after CHIP1.
    The goal of this analysis is to determine if this data is better than my previous runs
    by outputting graphs and statistics to a csv file. I can then compare those graphs and
    data to the previous design runs from CHIP1, aiming to have an expectation for the fluorescence
    output depending on the energies, geometry, and sequence of the protein.
'''

#TODO: change the below function: need to only look at the given interface positions on a sequence, not the overall interface sequence

def normalizeColumn(df, colName):
    '''This function will normalize a column in a dataframe'''
    # get the column
    col = df[colName]
    # normalize the column
    col = (col - col.min()) / (col.max() - col.min())
    # add the column back to the dataframe
    df[colName+'Norm'] = col
    # return the dataframe
    return df

# get the current directory
cwd = os.getcwd()

# get the config file options
kdeFile = sys.argv[1]
seqEntropyFile = sys.argv[2]
dataFile = sys.argv[3]
outputDir = sys.argv[4]
numSeqs = int(sys.argv[5])

# Read in the data from the csv file
df = pd.read_csv(dataFile, sep=',', header=0, dtype={'Interface': str})
listAA = ["A", "F", "G", "I", "L", "S", "T", "V", "W", "Y"]

# read in kde data as a dataframe
df_kde = pd.read_csv(kdeFile)

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

# lists for graphs
barGraphColList = ['Total', 'RepackChange', 'SasaDiff']
energyTerms = ['Total', 'HBONDDiff', 'VDWDiff', 'IMM1Diff']

# sort by total energy
df = df.sort_values(by=['Total'])
df = getRepackEnergies(df)
df = getGeomChanges(df)
#remove monomerWithoutAlaEnds col
#df = df.drop(columns=['MonomerWithoutAlaEnds'])
df.to_csv(outputDir+'/allData.csv', index=False)

# trim the data
df = df[df['Total'] < 0]
df = df[df['Total'] < df['TotalPreOptimize']]
df = df[df['OptimizeSasa'] < df['PreBBOptimizeSasa']]
df = df[df['SasaDiff'] < -600]
# normalize the sequence entropy
df = normalizeColumn(df, 'SequenceEntropy')
# set the sequence entropy limit
#seqEntropyLimit = 0.0001
#df = df[df['SequenceEntropyNorm'] < seqEntropyLimit]

# add region dataframes to a list
geomList = ['xShift', 'crossingAngle', 'axialRotationPrime', 'zShiftPrime']
df = addGeometricDistanceToDataframe(df, outputDir, geomList)

# shift the names of the geometry columns to be the same as the geomList
x, y, z, c = 'xShift', 'crossingAngle', 'zShift', 'axialRotation'
df = df.rename(columns={'endXShift': x, 'endCrossingAngle': y, 'endAxialRotationPrime': c, 'endZShiftPrime': z})

# make plot for the entire dataframe
allDir = f'{outputDir}/all'
os.makedirs(allDir, exist_ok=True)
makePlotsForDataframe(df, df_kde, allDir, 'all', barGraphColList, energyTerms)

df_avg = pd.DataFrame()
topSeqsDf = pd.DataFrame()

# df list for each region
df_neg = pd.DataFrame()
df_pos = pd.DataFrame()

# loop through each region
for region in df['Region'].unique():
    # add region column to start of df
    regionDir = f'{outputDir}/{region}'
    # make a directory for each region
    os.makedirs(regionDir, exist_ok=True)
    # get the region dataframe
    tmpDf = df[df['Region'] == region]
    # remove sequences where repack energy is greater than 0
    tmpDf = tmpDf[tmpDf['RepackChange'] < 0]
    makeInterfaceSeqLogo(tmpDf, regionDir)
    # sort by total energy
    tmpDf = tmpDf.sort_values(by=['Total'])
    # get the positive and negative hydrogen bonding dataframes
    tmpDf_pos, tmpDf_neg = tmpDf[tmpDf['HBONDDiff'] > 0], tmpDf[tmpDf['HBONDDiff'] < 0]
    # add to a list of dataframes
    dfs, dfNames = [tmpDf_pos, tmpDf_neg], ['posHbond', 'negHbond']
    for tmpDf,name in zip(dfs,dfNames):
        # make a new output directory combining the outputDir and name
        df_outputDir = f'{regionDir}/{name}'
        # make the output directory if it doesn't exist
        os.makedirs(df_outputDir, exist_ok=True)
        # plot the mean and standard deviation of the data for the given columns
        makePlotsForDataframe(tmpDf, df_kde, df_outputDir, name, barGraphColList, energyTerms)
        # output the dataframe to a csv file
        tmpDf.to_csv(f'{regionDir}/{region}_{name}.csv', index=False)
        # get the top sequences in Total Energy for each region 
        tmpDf_top = tmpDf.head(numSeqs)
        tmpDf_top.to_csv(f'{regionDir}/top_{numSeqs}_{name}.csv', index=False)
        # add the top sequences to a dataframe using concat
        topSeqsDf = pd.concat([topSeqsDf, tmpDf.head(50)])
        # check if name contains 'neg' to add to the appropriate dataframe
        if 'neg' in name:
            df_neg = pd.concat([df_neg, tmpDf])
        else:
            df_pos = pd.concat([df_pos, tmpDf])

# make plot for the entire dataframe
topDir = f'{outputDir}/top'
os.makedirs(topDir, exist_ok=True)
makePlotsForDataframe(topSeqsDf, df_kde, topDir, 'top', barGraphColList, energyTerms)

cols = ['VDWDiff', 'HBONDDiff', 'IMM1Diff', 'Total', 'GeometricDistance']
df_avg = getEnergyDifferenceDf(df, cols, 100)

df_neg_avg = getEnergyDifferenceDf(df_neg, cols, 100)
df_pos_avg = getEnergyDifferenceDf(df_pos, cols, 100)
plotEnergyDiffs(df_neg_avg, outputDir, 'neg')
plotEnergyDiffs(df_pos_avg, outputDir, 'pos')

df = getInterfaceSequence(df)
getAAPercentageComposition(df, seqEntropyFile, listAA, 'InterfaceSeq', outputDir)

# could I look at the geometries for sequences that have low hbond energy and high vdw energy?
# i think I need to do some comparisons and outputs for the top x sequences that I am interested in looking at?

# split each into high and low hbond energy
df_low = df[df['HBONDDiff'] < -5]
df_high = df[df['HBONDDiff'] > -5]
# sort by total energy
df_low = df_low.sort_values(by=['Total'])
df_high = df_high.sort_values(by=['Total'])
# output to a csv file without the index
df_low.to_csv(f'{outputDir}/lowHbond.csv', index=False)
df_high.to_csv(f'{outputDir}/highHbond.csv', index=False)

df_low_avg = getEnergyDifferenceDf(df_low, cols, 100)
df_high_avg = getEnergyDifferenceDf(df_high, cols, 100)
plotEnergyDiffs(df_low_avg, outputDir, 'lowHbond')
plotEnergyDiffs(df_high_avg, outputDir, 'highHbond')

# reset plot
plt.clf()

"""
    - compare geometries from duplicate sequences
    - compare geometries from non-duplicate sequences (kde plots for this and above?)\
    - scatterplots of predicted fluorescence...?
    - overlay of kde plots for CHIP1 vs now; maybe overlay of geometries that worked in CHIP1
    - bar graph of each of the terms with mean total energy for the top 100 sequences for each region
"""
