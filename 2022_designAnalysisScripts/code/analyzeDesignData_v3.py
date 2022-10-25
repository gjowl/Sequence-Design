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
df.to_csv(outputDir+'/allData.csv')

# trim the data
df = df[df['Total'] < -10]
df = df[df['Total'] < df['TotalPreBBOptimize']]
# any other ways to trim? SASA score? 
df['repackEnergyDifference'] = df['Total'] - df['TotalPreBBOptimize']

# divide data into dataframes for each region
df_GAS = df[df['Region'] == 'GAS']
df_Left = df[df['Region'] == 'Left']
df_Right = df[df['Region'] == 'Right']

# add region dataframes to a list
df_list = [df_GAS, df_Left, df_Right]
geomList = ['xShift', 'crossingAngle', 'axialRotationPrime', 'zShiftPrime']
df_list = addGeometricDistanceToDataframe(df_list, outputDir, geomList)

# analyze the repack energy
# loop through each region
df_avg = pd.DataFrame()
for df in df_list:
    tmpDf = getRepackEnergies(df)
    tmpDf = getGeomChanges(tmpDf)
    region = tmpDf['Region'].values[0]
    dir = outputDir + '/' + region
    # make a directory for each region
    if not os.path.exists(dir):
        os.makedirs(dir)
    # get the top 100 sequences in Total Energy for each region
    tmpDf = tmpDf[tmpDf['geometryNumber'] > 0]
    # remove sequences where repack energy is greater than 0
    tmpDf = tmpDf[tmpDf['repackEnergyDifference'] < 0]
    # rid of anything with geometric distance > 0.5
    tmpDf = tmpDf[tmpDf['GeometricDistance'] < 0.5]
    # loop through each geometryNumber
    outputFile = dir + '/repackEnergyAnalysis.png'
    plotMeanAndSDBarGraph(tmpDf, outputFile, 'geometryNumber', 'repackEnergyDifference')
    # get average VDWDiff, HBONDDiff, and IMM1Diff from the top 100 sequences
    avgVDWDiff, sdVDW = tmpDf['VDWDiff'].mean(), tmpDf['VDWDiff'].std()
    avgHBONDDiff, sdHBOND = tmpDf['HBONDDiff'].mean(), tmpDf['HBONDDiff'].std()
    avgIMM1Diff, sdIMM1 = tmpDf['IMM1Diff'].mean(), tmpDf['IMM1Diff'].std()
    avgEntropy, sdEntropy = tmpDf['EntropyChange'].mean(), tmpDf['EntropyChange'].std()
    avgTotal, sdTotal = tmpDf['Total'].mean(), tmpDf['Total'].std()
    avgSasa, sdSasa = tmpDf['SASADiff'].mean(), tmpDf['SASADiff'].std()
    df_avg = pd.concat([df_avg, pd.DataFrame({'Region': [region], 'VDWDiff': [avgVDWDiff], 'sdVDW': [sdVDW], 'HBONDDiff': [avgHBONDDiff], 'sdHBOND': [sdHBOND], 'IMM1Diff': [avgIMM1Diff], 'sdIMM1': [sdIMM1], 'Entropy': [avgEntropy], 'sdEntropy': [sdEntropy], 'Total': [avgTotal], 'sdTotal': [sdTotal], 'SASADiff': [avgSasa], 'sdSASA': [sdSasa]})], ignore_index=True)
    plotGeomKde(df_kde, tmpDf, 'Total', outputDir, 'startXShift', 'startCrossingAngle', region)
    bestDf = tmpDf.head(50)
    bestDf.to_csv(outputDir+'/top50_'+bestDf['Region'].iloc[0]+'.csv')
# from here, start defining what data I want to keep: geometric distance < 0.5
# rid of anything with Total > 0 and repack energy > 0
df = df[df['VDWDimer'] < 0]
plotEnergyDiffs(df_avg, outputDir)

listAA = ["A", "F", "G", "I", "L", "S", "T", "V", "W", "Y"]
# make a dictionary of amino acids and the number of times they appear in the top 100 sequences
# 
seqCountDfList = []
for df in df_list:
    aaDict = {}
    for aa in listAA:
        aaDict[aa] = 0
    for index, row in df.iterrows():
        for aa in listAA:
            aaDict[aa] += row['Sequence'].count(aa)
            # count the number of times each amino acid appears in the top 100 sequences in the interface
            aaDict[aa] += row['InterfaceSequence'].count(aa)
    # make a dataframe of the amino acid dictionary
    df_aa = pd.DataFrame.from_dict(aaDict, orient='index', columns=['Count'])
    # sum the total number of amino acids
    df_aa['Total'] = df_aa['Count'].sum()
    # get the percentage of each amino acid by dividing the count by the total
    df_aa['Percent'] = df_aa['Count'] / df_aa['Total']
    # add to the list of dataframes
    seqCountDfList.append(df_aa)

ind = np.arange(len(seqCountDfList))
width = 0.25
# make a bar graph of the amino acid percentages
fig, ax = plt.subplots()
# get the amino acid percentages for each region
GAS = seqCountDfList[0]['Percent']
print(GAS)
rects1 = ax.bar(ind, GAS, width, color='r')
rects2 = ax.bar(ind + width, seqCountDfList[1]['Percent'], width, color='g')
rects3 = ax.bar(ind + width*2, seqCountDfList[2]['Percent'], width, color='b')
ax.set_ylabel('Percent')
ax.set_title('Amino Acid Percentages')
ax.set_xticks(ind + width)
ax.set_xticklabels(seqCountDfList[0].index)
ax.legend((rects1[0], rects2[0], rects3[0]), ('GAS', 'Left', 'Right'))
plt.savefig(outputDir + '/aminoAcidPercentages.png')
plt.close()

    #df_aa = df_aa.sort_values(by=['Count'], ascending=False)
    #df_aa.to_csv(outputDir+'/aaCount.csv')

#for df in df_list:
#    outputDf = pd.DataFrame()
#    # trim the sequence column to residues 4-18
#    df['Sequence'] = df['Sequence'].str[3:17]
#    for aa in listAA:
#        outputDf[aa] = df['Sequence'].str.count(aa)
#        #outputDf[aa] = df['InterfaceSequence'].str.count(aa)
#    
#    outputDf['Sequence'] = df['Sequence']
#    region = df['Region'].iloc[0]
#    dir = outputDir + '/' + region
#    outputFile = dir+'/sequenceComposition.csv'
#    # print outputDf to csv
#    outputDf.to_csv(outputFile, index=False)

# ideas for analysis
"""
    - compare geometries from duplicate sequences
    - compare geometries from non-duplicate sequences (kde plots for this and above?)\
    - scatterplots of predicted fluorescence...?
    - overlay of kde plots for CHIP1 vs now; maybe overlay of geometries that worked in CHIP1
    - bar graph of each of the terms with mean total energy for the top 100 sequences for each region
"""
