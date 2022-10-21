import pandas as pd
import sys
import os
import numpy as np
from functions_v2 import *
import matplotlib.pyplot as plt
import matplotlib.colors

'''
    This file is used to analyze the data from my second set of design runs after CHIP1.
    The goal of this analysis is to determine if this data is better than my previous runs
    by outputting graphs and statistics to a csv file. I can then compare those graphs and
    data to the previous design runs from CHIP1, aiming to have an expectation for the fluorescence
    output depending on the energies, geometry, and sequence of the protein.
'''

# Read in the data from the csv file
df = pd.read_csv(sys.argv[1], sep=',', header=0)
kdeFile = os.getcwd()+'/' + '2020_09_23_kdeData.csv'

# read in kde data as a dataframe
df_kde = pd.read_csv(kdeFile)

# Set up output directory
outputDir = setupOutputDir(sys.argv[1])

# only keep the unique sequence with best total energy
df = df.sort_values(by=['Total'], ascending=True)
df = df.drop_duplicates(subset=['Sequence'], keep='first')

# loop through dataframe rows
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
df.to_csv(outputDir+'/allData.csv')

# get the top 100 sequences in Total Energy for each region
df_GAS = df[df['Region'] == 'GAS']
df_Left = df[df['Region'] == 'Left']
df_Right = df[df['Region'] == 'Right']

# add region dataframes to a list
df_list = [df_GAS, df_Left, df_Right]
df_list = addGeometricDistanceToDataframe(df_list, outputDir)

# rid of anything with Total > 0 and repack energy > 0
df = df[df['Total'] < -10]
df = df[df['VDWDimer'] < 0]

# output the dataframes to csv files
for df in df_list:
    # rid of anything with geometric distance > 1
    df = df[df['GeometricDistance'] < 1]
    # sort by total energy
    df = df.sort_values(by=['Total'])
    # get the top 100 sequences in Total Energy
    df = df.head(100)
    df.to_csv(outputDir+'/top100_'+df['Region'].iloc[0]+'.csv')

df_avg = pd.DataFrame()
# loop through the region dataframes
for df in df_list:
    tmpDf = getRepackEnergies(df)
    tmpDf = getGeomChanges(tmpDf)
    # get region name
    region = df['Region'].iloc[0]
    # get average VDWDiff, HBONDDiff, and IMM1Diff from the top 100 sequences
    avgVDWDiff, sdVDW = tmpDf['VDWDiff'].mean(), tmpDf['VDWDiff'].std()
    avgHBONDDiff, sdHBOND = tmpDf['HBONDDiff'].mean(), tmpDf['HBONDDiff'].std()
    avgIMM1Diff, sdIMM1 = tmpDf['IMM1Diff'].mean(), tmpDf['IMM1Diff'].std()
    avgEntropy, sdEntropy = tmpDf['EntropyChange'].mean(), tmpDf['EntropyChange'].std()
    avgTotal, sdTotal = tmpDf['Total'].mean(), tmpDf['Total'].std()
    avgSasa, sdSasa = tmpDf['SASADiff'].mean(), tmpDf['SASADiff'].std()
    # add the region and average VDWDiff, HBONDDiff, IMM1Diff, and Total to dataframe using concat
    df_avg = pd.concat([df_avg, pd.DataFrame({'Region': [region], 'VDWDiff': [avgVDWDiff], 'sdVDW': [sdVDW], 'HBONDDiff': [avgHBONDDiff], 'sdHBOND': [sdHBOND], 'IMM1Diff': [avgIMM1Diff], 'sdIMM1': [sdIMM1], 'Entropy': [avgEntropy], 'sdEntropy': [sdEntropy], 'Total': [avgTotal], 'sdTotal': [sdTotal], 'SASADiff': [avgSasa], 'sdSASA': [sdSasa]})], ignore_index=True)
    #df_avg = pd.concat([df_avg, pd.DataFrame({'Region': [region], 'VDWDiff': [avgVDWDiff], 'sdVDW': [sdVDW], 'HBONDDiff': [avgHBONDDiff], 'sdHBOND': [sdHBOND], 'IMM1Diff': [avgIMM1Diff], 'sdIMM1': [sdIMM1], 'Entropy': [avgEntropy], 'sdEntropy': [sdEntropy], 'Total': [avgTotal], 'sdTotal': [sdTotal]})])
    #df_avg = pd.concat([df_avg, pd.DataFrame({'Region': [region], 'VDWDiff': [avgVDWDiff], 'sdVDW': [sdVDW], 'HBONDDiff': [avgHBONDDiff], 'sdHBOND': [sdHBOND], 'IMM1Diff': [avgIMM1Diff], 'sdIMM1': [sdIMM1], 'Total': [avgTotal], 'sdTotal': [sdTotal]})])
    plotGeomKde(df_kde, df, 'Total', outputDir, 'startXShift', 'startCrossingAngle', region)
    #plotHist(df, 'Total',outputDir, region)

plotMeanAndSDBarGraph(df, outputDir, 'geometryNumber', 'VDWDiff')
plotEnergyDiffs(df_avg, outputDir)
listAA = ["A", "F", "G", "I", "L", "S", "T", "V", "W", "Y"]
for df in df_list:
    outputDf = pd.DataFrame()
    # trim the sequence column to residues 4-18
    df['Sequence'] = df['Sequence'].str[3:17]
    for aa in listAA:
        outputDf[aa] = df['Sequence'].str.count(aa)
    outputDf['Sequence'] = df['Sequence']
    region = df['Region'].iloc[0]
    outputFile = outputDir+"/"+region+'_sequenceComposition.csv'
    # print outputDf to csv
    outputDf.to_csv(outputFile, index=False)

# output the top 100 sequences to a csv file
df_top.to_csv(outputDir+'/top100.csv')
exit(0)

# ideas for analysis
"""
    - compare geometries from duplicate sequences
    - compare geometries from non-duplicate sequences (kde plots for this and above?)\
    - scatterplots of predicted fluorescence...?
    - overlay of kde plots for CHIP1 vs now; maybe overlay of geometries that worked in CHIP1
    - bar graph of each of the terms with mean total energy for the top 100 sequences for each region
"""
