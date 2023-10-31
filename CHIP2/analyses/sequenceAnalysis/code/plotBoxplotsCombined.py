'''
File: d:\github\Sequence-Design\CHIP2\analyses\sequenceAnalsysis\code\plotBoxplotsPerAAPosition.py
Project: d:\github\Sequence-Design\CHIP2\analyses\sequenceAnalsysis\code
Created Date: Sunday October 22nd 2023
Author: gjowl
-----
Last Modified: Sunday October 22nd 2023 2:16:24 pm
Modified By: gjowl
-----
Description:
-----
'''

import os, sys, pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns
from boxplotFunctions import plotBoxplot, plotMultiBoxplot

def filterDf(input_df, col1, col2):
    # remove any values that have less than 1 sequence for either wt or mut
    tmp_df = input_df.groupby(col1).filter(lambda x: len(x) > number_sequence_cutoff).copy()
    for val in tmp_df[col1].unique():
        tmp_df_val = tmp_df[tmp_df[col1] == val]
        for t in tmp_df_val[col2].unique():
            tmp_df_val_type = tmp_df_val[tmp_df_val[col2] == t]
            if len(tmp_df_val_type) < 1:
                # remove the mutAA from the tmp_df
                tmp_df = tmp_df[tmp_df[col1] != val]
    return tmp_df

# read in the command line arguments
sequenceFile = sys.argv[1]
outputDir = sys.argv[2]

# read in the input files
df_seq = pd.read_csv(sequenceFile) # wt data file

# make the output directory
os.makedirs(outputDir, exist_ok=True)

yaxis = 'PercentGpA'
xaxis = 'Sample'

# plot the boxplots
filename = os.path.basename(sequenceFile).split('.')[0]

# remove anything with no sample name (TODO: figure out why this is happening)
df_seq = df_seq[df_seq['Sample'].notnull()]
df_seq.sort_values(by='Type', inplace=True)
plotBoxplot(df_seq, xaxis, yaxis, outputDir, filename)
plotMultiBoxplot(df_seq, xaxis, yaxis, 'Type', outputDir, filename)

df_seq['pos_wtAA'] = df_seq['Position'].astype(str) + df_seq['WT_AA']
df_seq['pos_mutAA'] = df_seq['Position'].astype(str) + df_seq['mut_AA']
df_seq['WT_MUT'] = df_seq['WT_AA'] + df_seq['mut_AA']

number_sequence_cutoff = 5
cols_to_plot = ['Position', 'WT_AA', 'mut_AA', 'pos_wtAA', 'pos_mutAA', 'WT_MUT']
for sample in df_seq['Sample'].unique():
    df_sample = df_seq[df_seq['Sample'] == sample]
    sample_outputDir = f'{outputDir}/{sample}'
    os.makedirs(sample_outputDir, exist_ok=True)
    df_sample.sort_values(by='Type', inplace=True)
    plotMultiBoxplot(df_sample, xaxis, yaxis, 'Type', outputDir, filename)
    tmp_df = df_sample.groupby('mut_AA').filter(lambda x: len(x) > number_sequence_cutoff).copy()
    # only keep the mut_AA that have more than 1 sequence for both wt and mut
    # remove any mut_AA that have less than 1 sequence for either wt or mut
    plotBoxplot(tmp_df, 'mut_AA', yaxis, sample_outputDir, filename)
    # only keep rows that have > number_sequence_cutoff posMutAA
    tmp_df = df_sample.groupby('pos_mutAA').filter(lambda x: len(x) > number_sequence_cutoff).copy()
    plotBoxplot(tmp_df, 'pos_mutAA', yaxis, sample_outputDir, filename)
    # make a column for wt_percentGpA that gets the vale from the df_wt_sample for matching sequences
    #tmp_df['wt_percentGpA'] = tmp_df.apply(lambda row: df_wt_sample[df_wt_sample['Sequence'] == row['Sequence']][yaxis].values[0], axis=1)
    tmp_df1 = tmp_df.groupby('pos_wtAA').filter(lambda x: len(x) > number_sequence_cutoff).copy()
    plotBoxplot(tmp_df1, 'Position', yaxis, sample_outputDir, filename)
    for mutant_type in df_sample['Mutant Type'].unique():
        df_mutant_type = df_sample[df_sample['Mutant Type'] == mutant_type]
        mut_outputDir = f'{sample_outputDir}/{mutant_type}'
        os.makedirs(mut_outputDir, exist_ok=True)
        for col in cols_to_plot:
            tmp_df = filterDf(df_mutant_type, col, 'Type')
            tmp_df.sort_values(by='Type', inplace=True)
            plotMultiBoxplot(tmp_df, col, yaxis, 'Type', mut_outputDir, filename)

for col in cols_to_plot:
    plotMultiBoxplot(df_seq, col, yaxis, 'Type', outputDir, filename)

for mutant_type in df_seq['Mutant Type'].unique():
    df_mutant_type = df_seq[df_seq['Mutant Type'] == mutant_type]
    mut_outputDir = f'{outputDir}/{mutant_type}'
    os.makedirs(mut_outputDir, exist_ok=True)
    for col in cols_to_plot:
        tmp_df = filterDf(df_mutant_type, col, 'Type')
        tmp_df.sort_values(by='Type', inplace=True)
        plotMultiBoxplot(tmp_df, col, yaxis, 'Type', mut_outputDir, filename)