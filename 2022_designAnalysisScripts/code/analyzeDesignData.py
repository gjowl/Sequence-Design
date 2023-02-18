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

# sort by total energy
df = df.sort_values(by=['Total'])
df = getRepackEnergies(df)
df = getGeomChanges(df)
df.to_csv(outputDir+'/allData.csv')

# trim the data
df = df[df['Total'] < 0]
df = df[df['Total'] < df['TotalPreOptimize']]
df = df[df['OptimizeSasa'] < df['PreBBOptimizeSasa']]
df = df[df['SasaDiff'] < -600]
# check to see if IMM1Diff is not empty
#if df[df['IMM1Diff'] != 0] is not empty:
#    df = df[df['IMM1Diff'] > 10]
#df = df[df['IMM1Diff'] > 10]
# normalize the sequence entropy
df = normalizeColumn(df, 'SequenceEntropy')
# set the sequence entropy limit
#seqEntropyLimit = 0.0001
#df = df[df['SequenceEntropyNorm'] < seqEntropyLimit]

# add region dataframes to a list
geomList = ['xShift', 'crossingAngle', 'axialRotationPrime', 'zShiftPrime']
df = addGeometricDistanceToDataframe(df, outputDir, geomList)

# make plot for the entire dataframe
makePlotsForDataframe(df, df_kde, outputDir, 'all')

# loop through each region
df_avg = pd.DataFrame()
topSeqsDf = pd.DataFrame()
for region in df['Region'].unique():
    # add region column to start of df
    regionDir = f'{outputDir}/{region}'
    # make a directory for each region
    if not os.path.exists(regionDir):
        os.makedirs(regionDir)
    # get the region dataframe
    tmpDf = df[df['Region'] == region]
    # get the top 100 sequences in Total Energy for each region
    #tmpDf = df[df['geometryNumber'] > 0]
    # remove sequences where repack energy is greater than 0
    tmpDf = tmpDf[tmpDf['RepackChange'] < 0]
    # sort by total energy
    tmpDf = tmpDf.sort_values(by=['Total'])
    # separate the dataframe with positive and negative hydrogen bonding
    tmpDf_pos = tmpDf[tmpDf['HBONDDiff'] > 0]
    tmpDf_neg = tmpDf[tmpDf['HBONDDiff'] < 0]
    # output the dataframe to a csv file
    tmpDf_neg.to_csv(f'{regionDir}/{region}_Data_negativeHbond.csv', index=False)
    tmpDf_pos.to_csv(f'{regionDir}/{region}_Data_positiveHbond.csv', index=False)
    makePlotsForDataframe(tmpDf_neg, df_kde, regionDir, 'negativeHbond')
    makePlotsForDataframe(tmpDf_pos, df_kde, regionDir, 'positiveHbond')
    # get the top sequences in Total Energy for each region 
    tmpDf_neg = tmpDf_neg.head(numSeqs)
    tmpDf_pos = tmpDf_pos.head(numSeqs)
    tmpDf_neg.to_csv(f'{outputDir}/top_{numSeqs}_{region}_neg.csv', index=False)
    tmpDf_pos.to_csv(f'{outputDir}/top_{numSeqs}_{region}_pos.csv', index=False)
    # add the top sequences to a dataframe using concat
    topSeqsDf = pd.concat([topSeqsDf, tmpDf_neg.head(50)])

# make plot for the entire dataframe
makePlotsForDataframe(topSeqsDf, df_kde, outputDir, 'top150')

cols = ['VDWDiff', 'HBONDDiff', 'IMM1Diff', 'Total', 'GeometricDistance']
df_avg = getEnergyDifferenceDf(df, cols, 100)

plotEnergyDiffs(df_avg, outputDir)

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
# output to a csv file
df_low.to_csv(f'{outputDir}/lowHbond.csv')
df_high.to_csv(f'{outputDir}/highHbond.csv')


"""
    - compare geometries from duplicate sequences
    - compare geometries from non-duplicate sequences (kde plots for this and above?)\
    - scatterplots of predicted fluorescence...?
    - overlay of kde plots for CHIP1 vs now; maybe overlay of geometries that worked in CHIP1
    - bar graph of each of the terms with mean total energy for the top 100 sequences for each region
"""
