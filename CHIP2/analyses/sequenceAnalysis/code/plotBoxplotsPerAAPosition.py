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
from boxplotFunctions import plotBoxplot

# read in the command line arguments
sequenceFile = sys.argv[1]
mutantFile = sys.argv[2]
outputDir = sys.argv[3]

# read in the input files
df_wt = pd.read_csv(sequenceFile) # wt data file
df_mut = pd.read_csv(mutantFile) # mutant data file

# make the output directory
os.makedirs(outputDir, exist_ok=True)

#yaxis = 'PercentGpA_transformed'
yaxis = 'PercentGpA'
xaxis = 'Sample'

# plot the boxplots
wt_filename = os.path.basename(sequenceFile).split('.')[0]
mut_filename = os.path.basename(mutantFile).split('.')[0]
plotBoxplot(df_wt, xaxis, yaxis, outputDir, wt_filename)
plotBoxplot(df_mut, xaxis, yaxis, outputDir, mut_filename)

df_mut['pos_wtAA'] = df_mut['Position'].astype(str) + df_mut['WT_AA']
# get the mutant aa for each sequence, based on the position column
df_mut['mut_AA'] = df_mut.apply(lambda row: row['Mutant'][row['Position']], axis=1)
df_mut['pos_mutAA'] = df_mut['Position'].astype(str) + df_mut['mut_AA']

number_sequence_cutoff = 5
for sample in df_mut['Sample'].unique():
    df_sample = df_mut[df_mut['Sample'] == sample]
    sample_outputDir = f'{outputDir}/{sample}'
    os.makedirs(sample_outputDir, exist_ok=True)
    # combine the position and mutant AA
    tmp_df = df_sample.groupby('mut_AA').filter(lambda x: len(x) > number_sequence_cutoff).copy()
    plotBoxplot(tmp_df, 'mut_AA', yaxis, sample_outputDir, mut_filename)
    # only keep rows that have > number_sequence_cutoff posMutAA
    tmp_df = df_sample.groupby('pos_mutAA').filter(lambda x: len(x) > number_sequence_cutoff).copy()
    plotBoxplot(tmp_df, 'pos_mutAA', yaxis, sample_outputDir, mut_filename)
    # get the sequences from the df_wt that are present in the df_sample
    df_wt_sample = df_wt[df_wt['Sequence'].isin(df_sample['Sequence'])]
    tmp_df = df_sample[df_sample['Sequence'].isin(df_wt_sample['Sequence'])].copy()
    # make a column for wt_percentGpA that gets the vale from the df_wt_sample for matching sequences
    tmp_df['wt_percentGpA'] = tmp_df.apply(lambda row: df_wt_sample[df_wt_sample['Sequence'] == row['Sequence']][yaxis].values[0], axis=1)
    tmp_df1 = tmp_df.groupby('pos_wtAA').filter(lambda x: len(x) > number_sequence_cutoff).copy()
    plotBoxplot(tmp_df1, 'Position', yaxis, sample_outputDir, mut_filename)
    # keep only unique sequences
    tmp_df1 = tmp_df1.drop_duplicates(subset=['Sequence'])
    plotBoxplot(tmp_df1, 'mut_AA', 'wt_percentGpA', sample_outputDir, mut_filename)
    plotBoxplot(tmp_df1, 'pos_wtAA', 'wt_percentGpA', sample_outputDir, mut_filename)
    plotBoxplot(tmp_df1, 'Position', 'wt_percentGpA', sample_outputDir, mut_filename)
    tmp_df1 = tmp_df.groupby('pos_mutAA').filter(lambda x: len(x) > number_sequence_cutoff).copy()
    tmp_df1 = tmp_df1.drop_duplicates(subset=['Sequence'])
    plotBoxplot(tmp_df1, 'pos_mutAA', 'wt_percentGpA', sample_outputDir, mut_filename)
    # calculate the difference between the wt and mutant
    tmp_df['diff'] = tmp_df['wt_percentGpA'] - tmp_df[yaxis]
    # get the average difference for each position
    tmp_df['Average_diff'] = tmp_df.groupby('pos_wtAA')['diff'].transform('mean')
    # get the percent difference for each position by dividing the average difference by the top wt_percentGpA
    tmp_df['Percent_diff'] = tmp_df['Average_diff'] / tmp_df.groupby('pos_wtAA')['wt_percentGpA'].transform('max')
    tmp_df1 = tmp_df.groupby('pos_wtAA').filter(lambda x: len(x) > number_sequence_cutoff).copy()
    # output to a csv
    tmp_df1.to_csv(f'{sample_outputDir}/{sample}.csv', index=False)
    # print the top 5 highest and lowest average difference and position_wtAA
    #print(sample)
    #print(tmp_df1.groupby('pos_wtAA')['Percent_diff'].mean().sort_values(ascending=False).head(5))
    #print(tmp_df1.groupby('pos_wtAA')['Percent_diff'].mean().sort_values(ascending=True).head(5))

    #tmp_df1 = tmp_df.groupby('pos_mutAA').filter(lambda x: len(x) > 10).copy()
    #plotBoxplot(tmp_df1, 'pos_mutAA', 'diff', sample_outputDir, mut_filename, ybottom=-0.5, ytop=0.5)
    #tmp_df1 = tmp_df.groupby('pos_wtAA').filter(lambda x: len(x) > 10).copy()
    #plotBoxplot(tmp_df1, 'pos_wtAA', 'diff', sample_outputDir, mut_filename, ybottom=-0.5, ytop=0.5)
    #tmp_df1 = tmp_df.groupby('Position').filter(lambda x: len(x) > 10).copy()
    #plotBoxplot(tmp_df1, 'Position', 'diff', sample_outputDir, mut_filename)
    #for position in tmp_df['Position'].unique():
    #    tmp_df_pos = tmp_df[tmp_df['Position'] == position]
    #    tmp_df_pos = tmp_df_pos.groupby('pos_mutAA').filter(lambda x: len(x) > 10).copy()
    #    posFilename = f'pos{position}'
    #    plotBoxplot(tmp_df_pos, 'pos_mutAA', 'wt_percentGpA', sample_outputDir, posFilename)
    #    plotBoxplot(tmp_df_pos, 'pos_wtAA', 'wt_percentGpA', sample_outputDir, posFilename)