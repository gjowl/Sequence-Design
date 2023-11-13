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
from scipy.stats import ttest_ind

def filterDf(input_df, col1, col2):
    # remove any values that have less than 1 sequence for either wt or mut
    tmp_df = input_df.groupby(col1).filter(lambda x: len(x) > number_sequence_cutoff).copy()
    for val in tmp_df[col1].unique():
        tmp_df_val = tmp_df[tmp_df[col1] == val]
        for t in tmp_df_val[col2].unique():
            tmp_df_val_type = tmp_df_val[tmp_df_val[col2] == t]
            if len(tmp_df_val_type) < 1:
                # remove the val from the tmp_df
                tmp_df = tmp_df[tmp_df[col1] != val]
                continue
    return tmp_df

def keepSignificantInGrouping(input_df, grouping_col, yaxis, p_value_cutoff=0.05):
    # loop through the wt_aa
    significant_groups = []
    p_values = []
    for group in input_df[grouping_col].unique():
        wt = input_df[(input_df[grouping_col] == group) & (input_df['Type'] == 'WT')]
        mut = input_df[(input_df[grouping_col] == group) & (input_df['Type'] == 'Mutant')]
        # calculate the p-value
        p_value = ttest_ind(wt[yaxis], mut[yaxis])[1]
        if p_value < p_value_cutoff:
            p_values.append(p_value)
            significant_groups.append(group)
    # keep only the aas in significant_aas
    output_df = input_df[input_df[grouping_col].isin(significant_groups)].copy()
    return output_df 

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
df_seq = df_seq[df_seq['PercentGpA'] > 0]
df_seq.sort_values(by='Type', inplace=True)
plotBoxplot(df_seq, xaxis, yaxis, outputDir, filename)
plotMultiBoxplot(df_seq, xaxis, yaxis, 'Type', outputDir, filename)

df_seq['pos_wtAA'] = df_seq['Position'].astype(str) + df_seq['WT_AA']
df_seq['pos_mutAA'] = df_seq['Position'].astype(str) + df_seq['mut_AA']
df_seq['WT_MUT'] = df_seq['WT_AA'] + df_seq['mut_AA']

number_sequence_cutoff = 10
cols_to_plot = ['Position', 'WT_AA', 'mut_AA', 'pos_wtAA', 'pos_mutAA', 'WT_MUT']

for sample in df_seq['Sample'].unique():
    df_sample = df_seq[df_seq['Sample'] == sample]
    #print(f'Total proteins: {len(df_sample)}')
    sample_outputDir = f'{outputDir}/{sample}'
    os.makedirs(sample_outputDir, exist_ok=True)
    #df_sample.sort_values(by='Type', inplace=True)
    df_sample.sort_values(by='Type')
    plotMultiBoxplot(df_sample, xaxis, yaxis, 'Type', sample_outputDir)
    for col in cols_to_plot:
        tmp_df = df_sample.groupby(col).filter(lambda x: len(x) > number_sequence_cutoff).copy()
        # get the wt_aas in WT type sequences
        wt_vals = tmp_df[tmp_df['Type'] == 'WT'][col].unique()
        # keep only values in the tmp_df that are in the wt_aas
        tmp_df = tmp_df[tmp_df[col].isin(wt_vals)].copy()
        tmp_df = keepSignificantInGrouping(tmp_df, col, yaxis)
        # check if the tmp_df is empty
        if tmp_df.empty:
            continue
        tmp_df.sort_values(by='Type', inplace=True)
        plotMultiBoxplot(tmp_df, col, yaxis, 'Type', sample_outputDir)
    for mutant_type in tmp_df['Mutant Type'].unique():
        df_mutant_type = tmp_df[tmp_df['Mutant Type'] == mutant_type]
        mut_outputDir = f'{sample_outputDir}/{mutant_type}'
        os.makedirs(mut_outputDir, exist_ok=True)
        for col in cols_to_plot:
            tmp_df1 = filterDf(df_mutant_type, col, 'Type')
            tmp_df1 = keepSignificantInGrouping(tmp_df1, col, yaxis)
            tmp_df1.sort_values(by='Type', inplace=True)
            plotMultiBoxplot(tmp_df1, col, yaxis, 'Type', mut_outputDir)
    
for col in cols_to_plot:
    tmp_df = keepSignificantInGrouping(df_seq, col, yaxis)
    wt_vals = [tmp_df[tmp_df['Type'] == 'WT'][col].unique()]
    # keep only values in the tmp_df that are in the wt_aas
    tmp_df = tmp_df[tmp_df[col].isin(wt_vals)].copy()
    tmp_df.sort_values(by='Type', inplace=True)
    plotMultiBoxplot(tmp_df, col, yaxis, 'Type', outputDir)

#for mutant_type in df_seq['Mutant Type'].unique():
#    df_mutant_type = df_seq[df_seq['Mutant Type'] == mutant_type]
#    mut_outputDir = f'{outputDir}/{mutant_type}'
#    os.makedirs(mut_outputDir, exist_ok=True)
#    for col in cols_to_plot:
#        tmp_df = filterDf(df_mutant_type, col, 'Type')
#        tmp_df.sort_values(by='Type', inplace=True)
#        plotMultiBoxplot(tmp_df, col, yaxis, 'Type', mut_outputDir, filename)

# added on 2023-11-1 to compare just wt and mutant to different mutant types
# convert the mutant type column to WT for any sequences that are type WT
df_seq['Mutant Type'] = df_seq.apply(lambda row: 'WT' if row['Type'] == 'WT' else row['Mutant Type'], axis=1)
# sort the dataframe by the mutant type in the order of clash, void, wt
df_seq['Mutant Type'] = df_seq['Mutant Type'].astype('category')
df_seq['Mutant Type'].cat.set_categories(['clash', 'void', 'WT'], inplace=True)
df_seq.sort_values(['Mutant Type'], inplace=True)
output_file = f'{filename}_all'
plotMultiBoxplot(df_seq, 'Sample', yaxis, 'Mutant Type', outputDir, output_file)