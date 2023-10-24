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

yaxis = 'PercentGpA_transformed'
xaxis = 'Sample'

# plot the boxplots
wt_filename = os.path.basename(sequenceFile).split('.')[0]
mut_filename = os.path.basename(mutantFile).split('.')[0]
plotBoxplot(df_wt, xaxis, yaxis, outputDir, wt_filename)
plotBoxplot(df_mut, xaxis, yaxis, outputDir, mut_filename)

df_mut['pos_wtAA'] = df_mut['Position'].astype(str) + df_mut['WT_AA']
# get the mutant aa for each sequence, based on the position column
df_mut['mut_AA'] = df_mut.apply(lambda row: row['Mutant'][row['Position']-1], axis=1)
df_mut['pos_mutAA'] = df_mut['Position'].astype(str) + df_mut['mut_AA']

for sample in df_mut['Sample'].unique():
    df_sample = df_mut[df_mut['Sample'] == sample]
    sample_outputDir = f'{outputDir}/{sample}'
    os.makedirs(sample_outputDir, exist_ok=True)
    plotBoxplot(df_sample, 'Position', yaxis, sample_outputDir, mut_filename)
    # combine the position and mutant AA
    tmp_df = df_sample.groupby('mut_AA').filter(lambda x: len(x) > 10).copy()
    plotBoxplot(tmp_df, 'mut_AA', yaxis, sample_outputDir, mut_filename)
    # only keep rows that have > 10 posMutAA
    tmp_df = df_sample.groupby('pos_mutAA').filter(lambda x: len(x) > 10).copy()
    plotBoxplot(tmp_df, 'pos_mutAA', yaxis, sample_outputDir, mut_filename)
    # get the sequences from the df_wt that are present in the df_sample
    df_wt_sample = df_wt[df_wt['Sequence'].isin(df_sample['Sequence'])]
    tmp_df = df_sample[df_sample['Sequence'].isin(df_wt_sample['Sequence'])].copy()
    # make a column for wt_percentGpA that gets the vale from the df_wt_sample for matching sequences
    tmp_df['wt_percentGpA'] = tmp_df.apply(lambda row: df_wt_sample[df_wt_sample['Sequence'] == row['Sequence']]['PercentGpA_transformed'].values[0], axis=1)
    # keep only unique sequences
    tmp_df1 = tmp_df.groupby('pos_mutAA').filter(lambda x: len(x) > 10).copy()
    plotBoxplot(tmp_df1, 'pos_mutAA', 'wt_percentGpA', sample_outputDir, mut_filename)
    tmp_df1 = tmp_df.groupby('pos_wtAA').filter(lambda x: len(x) > 10).copy()
    plotBoxplot(tmp_df1, 'pos_wtAA', 'wt_percentGpA', sample_outputDir, mut_filename)
    plotBoxplot(tmp_df, 'Position', 'wt_percentGpA', sample_outputDir, mut_filename)
    #for position in tmp_df['Position'].unique():
    #    tmp_df_pos = tmp_df[tmp_df['Position'] == position]
    #    tmp_df_pos = tmp_df_pos.groupby('pos_mutAA').filter(lambda x: len(x) > 10).copy()
    #    posFilename = f'pos{position}'
    #    plotBoxplot(tmp_df_pos, 'pos_mutAA', 'wt_percentGpA', sample_outputDir, posFilename)
    #    plotBoxplot(tmp_df_pos, 'pos_wtAA', 'wt_percentGpA', sample_outputDir, posFilename)
    
# TODO: look at the wt data as well by getting the 
#for sample in df_wt['Sample'].unique():
#    df_sample = df_wt[df_wt['Sample'] == sample]
#    plotBoxplot(df_sample, 'WT_AA', yaxis, sample_outputDir, wt_filename)
#    tmp_df = df_sample.groupby('pos_wtAA').filter(lambda x: len(x) > 10).copy()
#    plotBoxplot(tmp_df, 'pos_wtAA', yaxis, sample_outputDir, wt_filename)

