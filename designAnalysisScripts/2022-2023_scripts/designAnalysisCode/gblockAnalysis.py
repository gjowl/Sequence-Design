import sys
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pymol import cmd
from analysisFunctions import getAAPercentageComposition, getInterfaceSequence

# loop through the best files
def createPse(df, rawDataDir, outputFile):
    # loop through the entire dataframe
    for i in range(len(df)):
        # get the directory name
        dirName = df['Directory'][i]
        # get the design number by splitting the directory name by _
        designNum, repNum = dirName.split('_')[1], df['replicateNumber'][i]
        # get the replicate number
        repNum = df['replicateNumber'][i]
        # pdbName
        pdbName = designNum+'_'+str(repNum)
        # put together the filename
        dir = df['dir'][i] 
        filename = rawDataDir+'/'+dir+'/'+dirName+'/'+pdbName+'.pdb'
        # load the pdb file
        cmd.load(filename)
        # loop through the interface
        # this is fast, but kind of redundant: I should get a list of all of the interface pos and then loop through that
        for j in range(0, len(df['Interface'][i])):
            # if the interface is 1
            if df['Interface'][i][j] == '1':
                # select the current pdb
                cmd.select('interface', pdbName)
                # color the residue for the current pdb
                cmd.color('red', 'interface and resi '+str(j+23))
    # show spheres
    cmd.show('spheres')
    # save the session file
    cmd.save(outputFile+'.pse')
    # reset the pymol session
    cmd.reinitialize()

def makeInterfaceSeqLogo(df, outputDir):
    '''This function will make a logo of the interface sequence'''
    # check if there are unique interfaces
    if len(df['Interface'].unique()) > 1:
        for interface in df['Interface'].unique():
            tmpDf = df[df['Interface'] == interface]
            # get the interface sequences
            sequences = tmpDf['Sequence']
            # loop through the interface and keep only the amino acids that are in the interface
            interfaceSequences = []
            for seq in sequences:
                # loop through each position in the interface
                for j in range(len(str(interface))):
                    if str(interface)[j] == '0':
                        # replace the amino acid with a dash if it is not in the interface (if 0 at that position)
                        seq = seq[:j] + '-' + seq[j+1:]
                interfaceSequences.append(seq)
            mat = logomaker.alignment_to_matrix(interfaceSequences)
            # use logomaker to make the logo
            logo = logomaker.Logo(mat, font_name='Arial', color_scheme='hydrophobicity')
            # save the logo
            logo.fig.savefig(outputDir + '/interfaceSeqLogo_'+str(interface)+'.png')
    else:
        # get the interface sequences
        sequences = df['Sequence']
        # get the interface
        interfaces = df['Interface']
        # loop through the interface and keep only the amino acids that are in the interface
        interfaceSequences = []
        for interface in interfaces: 
            for seq in sequences:
                # loop through each position in the interface
                for j in range(len(str(interface))):
                    if str(interface)[j] == '0':
                        # replace the amino acid with a dash if it is not in the interface (if 0 at that position)
                        seq = seq[:j] + '-' + seq[j+1:]
                interfaceSequences.append(seq)
        mat = logomaker.alignment_to_matrix(interfaceSequences)
        # use logomaker to make the logo
        logo = logomaker.Logo(mat, font_name='Arial', color_scheme='hydrophobicity')
        # save the logo
        logo.fig.savefig(outputDir + '/interfaceSeqLogo.png')

def plotEnergyDiffs(df, outputDir):
    # data columns to plot
    n = len(df)
    x = np.arange(n)*3
    numBars = 4
    width = 1/numBars
    # get the VDW energy difference column
    VDWDiff = df['VDWDiff']
    # get the HBOND energy difference column
    HBONDDiff = df['HBONDDiff']
    # get the IMM1 energy difference column
    IMM1Diff = df['IMM1Diff']
    total = df['Total']
    # setup the bar plots for each energy difference
    fig, ax = plt.subplots()
    # plot the energy differences with standard deviation
    p1 = plt.bar(x-width*2, VDWDiff, width, yerr=df['VDWDiffSD'], color='cornflowerblue', edgecolor='black')
    p2 = plt.bar(x-width, HBONDDiff, width, yerr=df['HBONDDiffSD'], color='lightcoral', edgecolor='black')
    p3 = plt.bar(x, IMM1Diff, width, yerr=df['IMM1DiffSD'],color='palegreen', edgecolor='black')
    p4 = plt.bar(x+width, total, width, yerr=df['TotalSD'],color='thistle', edgecolor='black')
    # change the dpi to make the image smaller
    fig.set_dpi(2000)
    plt.ylabel('Energy')
    plt.title('Energy Plot')
    # add legend with the legend to the right of the plot
    plt.legend((p1[0], p2[0], p3[0], p4[0]), ('VDW', 'HBOND', 'IMM1', 'Total'), loc='center left', bbox_to_anchor=(1.0, 0.5))
    # set size so that the legend fits
    plt.gcf().set_size_inches(12, 5)
    # set x axis labels as regions
    plt.xticks(x, df['Region'])
    fig.savefig(outputDir+'/energyDiffPlot.png')
    plt.close()

def getMeanAndSDDf(df, colNames):
    tmpDf = pd.DataFrame()
    for col in colNames:
        mean, sd = df[col].mean(), df[col].std()
        tmpDf = pd.merge(tmpDf, pd.DataFrame({col: [mean], col+'SD': [sd]}), how='outer', left_index=True, right_index=True)
    return tmpDf

def getEnergyDifferenceDf(df, columns):
    # loop through each region
    outputDf = pd.DataFrame()
    for region in df['Region'].unique():
        # get the dataframe for the region
        tmpDf = df[df['Region'] == region]
        # sort the df by energy
        tmpDf = tmpDf.sort_values(by=['Total'])
        # get the mean and standard deviation for each column
        tmpDf = getMeanAndSDDf(tmpDf, columns)
        tmpDf['Region'] = region
        # concat the tmpDf to the outputDf
        outputDf = pd.concat([outputDf, tmpDf], axis=0, ignore_index=True)
    return outputDf

# read in the gblock file
gblockFile = sys.argv[1]
gblock_df = pd.read_csv(gblockFile, sep=',', header=0)

# read in the all data file
allDataFile = sys.argv[2]
allData_df = pd.read_csv(allDataFile, sep=',', header=0, dtype={'Interface': str})

# keep only the sequences that are in the gblock file and reset the index
allData_df = allData_df[allData_df['Sequence'].isin(gblock_df['Sequence'])].reset_index(drop=True)

# define the output directory as the directory of the gblock file
outputDir = os.path.dirname(gblockFile)

# define output file name
filename = os.path.basename(gblockFile).split('.')[0]

# define the output file
outputFile = outputDir+'/'+filename

# define the raw data directory
rawDataDir = "/data02/gloiseau/Sequence_Design_Project/DesignRun2"

# create the pymol session file
createPse(allData_df, rawDataDir, outputFile)

# plot energy differences
cols = ['VDWDiff', 'HBONDDiff', 'IMM1Diff', 'Total']
df_avg = getEnergyDifferenceDf(allData_df, cols)
plotEnergyDiffs(df_avg, outputDir)

# fix this: I need seq logos for entropy and non-entropy
listAA = ["A", "F", "G", "I", "L", "S", "T", "V", "W", "Y"]
seqEntropyFile = '/data/github/Sequence-Design/2022_designAnalysisScripts/inputFiles/2021_12_05_seqEntropies.csv'
df = getInterfaceSequence(allData_df)
getAAPercentageComposition(df, seqEntropyFile, listAA, 'InterfaceSeq', outputDir)

# loop through the different regions of the data frame
#for region in df['Region'].unique():
#    # get the data frame for the current region
#    region_df = df[df['Region'] == region]
#    # 
#    makeInterfaceSeqLogo(region_df, outputDir)