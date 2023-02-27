import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

"""
This script is a reanalysis of my CHIP1 data. I want to take a look at how sequences with similar or the same interface sequence,
number of interfacials, and entropy score compare to each other. This is something similar to what Phil Romero wanted me to do,
and I think if there's something interesting in the data, I should go talk to him about it and potentially analyze it further in
the way that he wants me to.
"""
def getAAPercentageComposition(df, percentCompositionFile, listAA, seqColumn, outputDir):
    # get the percentage composition of each amino acid in the sequence
    # read in the AA sequence composition data with columns: AA, Entropy
    mergedCountsDf = pd.read_csv(percentCompositionFile, sep=',', header=0)
    # loop through dataframe regions
    for region in df['Region'].unique():
        tmpDf = df[df['Region'] == region]
        # make a dictionary of amino acids
        aaDict = {}
        for aa in listAA:
            aaDict[aa] = 0
        for index, row in tmpDf.iterrows():
            for aa in listAA:
                # count the number of times each amino acid appears in the interface
                aaDict[aa] += row[seqColumn].count(aa)
        # make a dataframe of the amino acid dictionary with columns for AA and count
        tmpDf = pd.DataFrame.from_dict(aaDict, orient='index')
        tmpDf = tmpDf.reset_index()
        tmpDf.columns = ['AA', 'Count']
        # sum the total number of amino acids
        tmpDf['Total'] = tmpDf['Count'].sum()
        # get the percentage of each amino acid by dividing the count by the total
        tmpDf[region] = tmpDf['Count'] / tmpDf['Total']
        # add the region AA percentage to a merged dataframe
        mergedCountsDf = pd.merge(mergedCountsDf, tmpDf[['AA', region]], on='AA')
    # output the merged dataframe
    mergedCountsDf.to_csv(outputDir+'/aaPercentagesByRegion.csv')
    # plot the AA percentages for each region in a bar chart with different colors
    mergedCountsDf.plot.bar(x='AA', rot=0, color=['royalblue', 'firebrick', 'cornsilk', 'lightsalmon'], edgecolor='black')
    # set the plot size
    plt.gcf().set_size_inches(12, 5)
    plt.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
    plt.title('Amino Acid Percent Composition Per region')
    # add in y-axis label
    plt.ylabel('Percent')
    plt.savefig(outputDir+'/AApercentages_'+seqColumn+'.png')
    plt.close()

def getInterfaceSequence(df):
    outputDf = pd.DataFrame()
    for region in df['Region'].unique():
        tmpDf = df[df['Region'] == region].copy()
        interfaceSeqList = []
        for interface,seq in zip(tmpDf['Interface'], tmpDf['Sequence']):
            # loop through the interface and keep only the amino acids that are in the interface
            interfaceSeq = ''
            for i in range(len(str(interface))):
                if str(interface)[i] == '1':
                    interfaceSeq += seq[i]
            interfaceSeqList.append(interfaceSeq)
        tmpDf['InterfaceSeq'] = interfaceSeqList
        # concatenate the dataframes
        outputDf = pd.concat([outputDf, tmpDf])
    return outputDf

# get data file from command line
dataFile = sys.argv[1]

# Read in the data from the csv file
df = pd.read_csv(dataFile, sep=',', header=0)

# loop through dataframe rows and break down into regions; may have to change how this is broken down
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

df = getInterfaceSequence(df)
getAAPercentageComposition(df, seqEntropyFile, listAA, 'InterfaceSeq', outputDir)