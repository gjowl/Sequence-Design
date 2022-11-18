import pandas as pd
import sys
import os
import numpy as np
from functions_v3 import *
import matplotlib.pyplot as plt
import matplotlib.colors
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D
import logomaker
from functions import *

'''
    This file is used to analyze the data from my second set of design runs after CHIP1.
    The goal of this analysis is to determine if this data is better than my previous runs
    by outputting graphs and statistics to a csv file. I can then compare those graphs and
    data to the previous design runs from CHIP1, aiming to have an expectation for the fluorescence
    output depending on the energies, geometry, and sequence of the protein.
'''

#TODO: change the below function: need to only look at the given interface positions on a sequence, not the overall interface sequence
def makeInterfaceSeqLogo(df, outputDir):
    '''This function will make a logo of the interface sequence'''
    # get the interface sequences
    seq = df['InterfaceSequence']
    # get the 
    mat = logomaker.alignment_to_matrix(seq)
    # use logomaker to make the logo
    logo = logomaker.Logo(mat, font_name='Arial', color_scheme='hydrophobicity')
    # save the logo
    logo.fig.savefig(outputDir + '/interfaceSeqLogo.png')
    # close the figure
    plt.close()

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

# read in the config file
configFile = sys.argv[1]
globalConfig = read_config(configFile)
config = globalConfig['analyzeDesignData']
cwd = os.getcwd()

# get the config file options
kdeFile = config['kdeFile']
seqEntropyFile = config['seqEntropyFile']
dataFile = config['dataFile']
outputDir = config['outputDir']
numSeqs = int(config['numSeqs'])

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
seqEntropyLimit = 0.0001
df = df[df['SequenceEntropyNorm'] < seqEntropyLimit]

# add region dataframes to a list
geomList = ['xShift', 'crossingAngle', 'axialRotationPrime', 'zShiftPrime']
df = addGeometricDistanceToDataframe(df, outputDir, geomList)

# loop through each region
df_avg = pd.DataFrame()
cols = ['xShift_dist', 'crossingAngle_dist', 'axialRotationPrime_dist', 'zShiftPrime_dist']
for region in df['Region'].unique():
    # add region column to start of df
    dir = outputDir + '/' + region
    # make a directory for each region
    if not os.path.exists(dir):
        os.makedirs(dir)
    # get the region dataframe
    tmpDf = df[df['Region'] == region]
    # get the top 100 sequences in Total Energy for each region
    tmpDf = df[df['geometryNumber'] > 0]
    # remove sequences where repack energy is greater than 0
    tmpDf = tmpDf[tmpDf['RepackChange'] < 0]
    # rid of anything with geometric distance > 0.5
    #tmpDf = tmpDf[tmpDf['GeometricDistance'] < 1]
    # loop through each geometryNumber
    outputFile = dir + '/repackEnergyAnalysis.png'
    plotMeanAndSDBarGraph(tmpDf, outputFile, 'geometryNumber', 'RepackChange')
    outputFile = dir + '/SasaDiff.png'
    plotMeanAndSDBarGraph(tmpDf, outputFile, 'geometryNumber', 'SasaDiff')
    plotScatterMatrix(df, cols, dir)
    # set the below up to look at just the regions, not the whole geom
    plotGeomKde(df_kde, tmpDf, 'Total', dir, 'startXShift', 'startCrossingAngle')
    bestDf = tmpDf.head(numSeqs)
    bestDf.to_csv(outputDir+'/top'+str(numSeqs)+'_'+bestDf['Region'].iloc[0]+'.csv')
    # shift the names of the geometry columns to be the same as the geomList
    bestDf = bestDf.rename(columns={'endXShift': 'xShift', 'endCrossingAngle': 'crossingAngle', 'endAxialRotationPrime': 'axialRotation', 'endZShiftPrime': 'zShift'})
    x, y, z, c = 'xShift', 'crossingAngle', 'zShift', 'axialRotation'
    scatter3DWithColorbar(bestDf, x, y, z, c, dir)
    makeInterfaceSeqLogo(tmpDf, dir)
    # output the dataframe to a csv file
    tmpDf.to_csv(outputDir+'/'+region+'data.csv')

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
df_low.to_csv(outputDir+'/lowHbond.csv')
df_high.to_csv(outputDir+'/highHbond.csv')


"""
    - compare geometries from duplicate sequences
    - compare geometries from non-duplicate sequences (kde plots for this and above?)\
    - scatterplots of predicted fluorescence...?
    - overlay of kde plots for CHIP1 vs now; maybe overlay of geometries that worked in CHIP1
    - bar graph of each of the terms with mean total energy for the top 100 sequences for each region
"""
