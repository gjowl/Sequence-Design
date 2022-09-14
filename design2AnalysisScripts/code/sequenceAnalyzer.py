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

# get directory of the input file
inputDir = os.path.dirname(sys.argv[1])
if inputDir == '':
    inputDir = os.getcwd()
# Create Sequence Probability dictionary from input file
sequenceProbabilityFile = os.getcwd() + "/sequenceProbabilityFile.csv"
dfSeqProb = pd.read_csv(sequenceProbabilityFile, sep=",")

# make output directory
analysisDir = inputDir+'/sequenceAnalysis/'
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

# count number of A in sequence column
listAA = ["A", "F", "G", "I", "L", "S", "T", "V", "W", "Y"]
filenames = ['All', 'Right', 'Left', 'GasRight']
dfs = [df, df_right, df_left, df_gasright]
for filename, df in zip(filenames, dfs):
    outputDf = pd.DataFrame()
    for aa in listAA:
        outputDf[aa] = df['Sequence'].str.count(aa)
    outputFile = analysisDir+filename+'sequenceComposition.csv'
    # print outputDf to csv
    outputDf.to_csv(outputFile, index=False)

# maybe look and see if Josh has sequences that pass maltose test to look at their distribution to compare to?

