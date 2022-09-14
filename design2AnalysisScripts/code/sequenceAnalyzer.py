import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sequenceAnalyzerFunctions import *
from functions import *

# ideas for sequence analysis
"""
 - get the sequence composition by percentage of each amino acid
 - get the sequence composition by percentage of each amino acid in the first half of the sequence
 - get the sequence composition by percentage of each amino acid in the second half of the sequence
 - get the sequence composition by percentage of each amino acid in the every quarter of the sequence
 - get sequence composition per position for each amino acid  
"""

# read in data from csv file
df = pd.read_csv(sys.argv[1])
<<<<<<< HEAD
=======
# get name of file without the extension
fileName = os.path.splitext(os.path.basename(sys.argv[1]))[0]
>>>>>>> 526550a3041fc0669e9d118b0c727dbcc999064b

# get directory of the input file
inputDir = os.path.dirname(sys.argv[1])
if inputDir == '':
    inputDir = os.getcwd()
# Create Sequence Probability dictionary from input file
sequenceProbabilityFile = os.getcwd() + "/sequenceProbabilityFile.csv"
dfSeqProb = pd.read_csv(sequenceProbabilityFile, sep=",")

# make output directory
<<<<<<< HEAD
analysisDir = inputDir+'/sequenceAnalysis/'
=======
analysisDir = inputDir+'/sequenceAnalysis/'+fileName+'/'
>>>>>>> 526550a3041fc0669e9d118b0c727dbcc999064b
# check if the analysis directory exists
if not os.path.exists(analysisDir):
    os.makedirs(analysisDir)

# only keep sequences that pass maltose test (> -95)
#df = df[df['MaltosePercentDiff'] > -95]

# break into design regions
df_right, df_left, df_gasright = breakIntoDesignRegions(df)

# define 

## output file
#outputFile = os.path.join(inputDir, 'CHIP1_goodMaltose.csv')
#df.to_csv(outputFile, index=False)
#
#columnNames = ["Total", "VDWDiff", "HBONDDiff", "IMM1Diff", "xShift", "crossingAngle", "axialRotation", "zShift"]
#
## Setup the output writer for converting dataframes into a spreadsheet
#outFile = os.path.join(analysisDir, 'sequenceAnalysis.xlsx')
#writer = pd.ExcelWriter(outFile)
#
## convert interface
#convertInterfaceToX(df)
#
## get the sequence composition by percentage of each amino acid
#interfaceAnalyzer(df, columnNames, analysisDir, writer)
#interfaceSequenceCounts(df, dfSeqProb, columnNames, analysisDir, writer)

<<<<<<< HEAD
# count number of A in sequence column
=======
# count number of each AA in sequence column
>>>>>>> 526550a3041fc0669e9d118b0c727dbcc999064b
listAA = ["A", "F", "G", "I", "L", "S", "T", "V", "W", "Y"]
filenames = ['All', 'Right', 'Left', 'GasRight']
dfs = [df, df_right, df_left, df_gasright]
for filename, df in zip(filenames, dfs):
    outputDf = pd.DataFrame()
<<<<<<< HEAD
    for aa in listAA:
        outputDf[aa] = df['Sequence'].str.count(aa)
=======
    tmpDf = pd.DataFrame()
    for aa in listAA:
        tmpDf[aa] = df['Sequence'].str.count(aa)
    # sum each tmpDf column
    for aa in listAA:
        print(aa, tmpDf[aa].sum())
        s = tmpDf[aa].sum()
        # add sum to outputDf using concat
        outputDf = outputDf.append({'AA': aa, 'Count': s}, ignore_index=True)
    #outputDf = outputDf.append({'AA': 'Total', 'Count': outputDf['Count'].sum()}, ignore_index=True)
    # sum count column
    count = outputDf['Count'].sum()
    # divide each count by total count
    outputDf['Average'] = outputDf['Count']/count
>>>>>>> 526550a3041fc0669e9d118b0c727dbcc999064b
    outputFile = analysisDir+filename+'sequenceComposition.csv'
    # print outputDf to csv
    outputDf.to_csv(outputFile, index=False)

# maybe look and see if Josh has sequences that pass maltose test to look at their distribution to compare to?

<<<<<<< HEAD
=======
# get average sequenceEntropy
>>>>>>> 526550a3041fc0669e9d118b0c727dbcc999064b
