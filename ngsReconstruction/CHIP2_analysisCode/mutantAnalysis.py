'''
File: /home/loiseau@ad.wisc.edu/github/Sequence-Design/ngsReconstruction/code/mutantAnalysis.py
Project: /home/loiseau@ad.wisc.edu/github/Sequence-Design/ngsReconstruction/code
Created Date: Friday August 4th 2023
Author: loiseau
-----
Last Modified: Friday August 4th 2023 1:39:38 pm
Modified By: loiseau
-----
Description:  
This file uses the following as inputs:
    - reconstructed fluorescence dataframe 
    - file with mutants and WT sequences and corresponding terms (currently energy and/or SASA)
It compares the fluorescence of the mutants to the WT sequence and outputs a dataframe with the 
percent difference of the mutant to the WT sequence. 
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------
'''

import sys, os, pandas as pd, numpy as np, matplotlib.pyplot as plt

def graphFluorescence(input_df, output_file, energy_col, fluor_col, error_col, output_dir):
    # plot the WT sequence fluorescence vs the energy
    plt.scatter(input_df[energy_col], input_df[fluor_col])
    # plot the standard deviation
    plt.errorbar(input_df[energy_col], input_df[fluor_col], yerr=input_df[error_col], fmt='o', color='black', ecolor='lightgray', elinewidth=3, capsize=0)
    plt.ylabel(fluor_col)
    plt.xlabel(energy_col)
    plt.title(f'{energy_col} vs {fluor_col}')
    # draw a line of best fit
    m, b = np.polyfit(input_df[energy_col], input_df[fluor_col], 1)
    plt.plot(input_df[energy_col], m*input_df[energy_col] + b)
    # add the equation to the plot
    plt.text(0.5, 0.5, f'y = {m:.2f}x + {b:.2f}', horizontalalignment='center', verticalalignment='center', transform=plt.gca().transAxes)
    # calculate the correlation coefficient
    corr = np.corrcoef(input_df[energy_col], input_df[fluor_col])[0,1]
    plt.text(0.5, 0.4, f'r = {corr:.2f}', horizontalalignment='center', verticalalignment='center', transform=plt.gca().transAxes)
    plt.savefig(f'{outputDir}/{output_file}.png')
    plt.clf()

def graphVsFluorescence(input_df, sample_names, cols_to_graph, fluor_col, error_col, output_dir):
    # loop through each sample
    for sample in sample_names:
        df_sample = input_df[input_df['Sample'] == sample]
        for col in cols_to_graph:
            graphFluorescence(df_sample, f'{sample}_{col}', col, fluor_col, error_col, output_dir)

def mergeDataframes(df_fluor_seqs, df_fluor_mutant, df_sequence_no_duplicates, df_mutant_no_duplicates, cols_to_add):
    # add the mean fluorescence to the sequence dataframe
    df_sequence_no_duplicates = df_sequence_no_duplicates.merge(df_fluor_seqs[cols_to_add], on='Sequence', how='left')
    df_mutant_no_duplicates = df_mutant_no_duplicates.merge(df_fluor_mutant[cols_to_add], left_on='Mutant', right_on='Sequence', how='left')
    # The above adds a additional column? get rid of the extra sequence column
    df_mutant_no_duplicates = df_mutant_no_duplicates.drop(columns=['Sequence_y'])
    # rename the sequence column
    df_mutant_no_duplicates = df_mutant_no_duplicates.rename(columns={'Sequence_x': 'Sequence'})
    return df_sequence_no_duplicates, df_mutant_no_duplicates

def filterDataframes(df_fluor, df_sequence, df_mutant, cols_to_add):
    # rid of any segments that are not numerical (removes control sequences)
    df_fluor = df_fluor[pd.to_numeric(df_fluor['Segments'], errors='coerce').notnull()]
    # add 'ILI' to the end of each sequence so that it matches the sequences in the mutant and WT dataframes
    df_fluor['Sequence'] = df_fluor['Sequence'].apply(lambda x: x + 'ILI')
    # get the data for sequences that successfully fluoresce
    df_fluor_seqs = df_fluor[df_fluor['Sequence'].isin(df_sequence['Sequence'])]
    df_fluor_mutant = df_fluor[df_fluor['Sequence'].isin(df_mutant['Mutant'])]
    df_fluor_mutant = df_fluor_mutant[~df_fluor_mutant['Sequence'].isin(df_fluor_seqs['Sequence'])]
    df_fluor_seqs['Type'] = 'WT'
    df_fluor_mutant['Type'] = 'Mutant'
    #print(len(df_fluor))
    #print(len(df_fluor_seqs))
    #print(len(df_fluor_mutant))
    # merge the dataframes
    df_fluor_labeled = pd.concat([df_fluor_seqs, df_fluor_mutant])
    # keep the data for sequences that fluoresce
    df_sequence = df_sequence[df_sequence['Sequence'].isin(df_fluor_seqs['Sequence'])]
    df_mutant = df_mutant[df_mutant['Mutant'].isin(df_fluor_mutant['Sequence'])]
    df_mutant = df_mutant[~df_mutant['Mutant'].isin(df_sequence['Sequence'])]
    # remove duplicate sequences
    df_sequence_no_duplicates = df_sequence.drop_duplicates(subset='Sequence', keep='first')
    df_mutant_no_duplicates = df_mutant.drop_duplicates(subset='Mutant', keep='first')
    # merge the dataframes
    df_sequence_no_duplicates, df_mutant_no_duplicates = mergeDataframes(df_fluor_seqs, df_fluor_mutant, df_sequence_no_duplicates, df_mutant_no_duplicates, cols_to_add)
    return df_sequence_no_duplicates, df_mutant_no_duplicates, df_fluor_labeled


# read in the reconstructed fluorescence dataframe
fluorescenceFile = sys.argv[1]
sequenceFile = sys.argv[2]
mutantFile = sys.argv[3]
outputDir = sys.argv[4]

os.makedirs(outputDir, exist_ok=True)

gpa = 'LIIFGVMAGVIGT'
g83i = 'LIIFGVMAIVIGT'
#g83iCutoff = 20000

df_fluor = pd.read_csv(fluorescenceFile)
df_sequence = pd.read_csv(sequenceFile)
df_mutant = pd.read_csv(mutantFile)

# THIS CODE IS ANNOYING; FIX IT SO THAT YOU DON'T HAVE TO HARDCODE so much
cols_to_add = ['Sequence', 'mean_transformed', 'std_adjusted', 'Sample']
#cols_to_add = ['Sequence', 'Percent GpA', 'Percent Error', 'Sample']

maltose_col = 'LB-12H_M9-36H'
maltose_cutoff = -97
maltose_limit = 10000000
use_maltose = False
if use_maltose:
    df_fluor = df_fluor[df_fluor[maltose_col] > maltose_cutoff]
    df_fluor = df_fluor[df_fluor[maltose_col] < maltose_limit]

# std cutoff
#percent_error_cutoff = 10
#df_fluor = df_fluor[df_fluor['Percent Error'] < percent_error_cutoff]
df_fluor['std_adjusted'] = df_fluor['mean_transformed'] * df_fluor['Percent Error'] / 100
#
## filter out by percent GpA
#percent_GpA_cutoff = 120
#df_fluor = df_fluor[df_fluor['Percent GpA'] < percent_GpA_cutoff]
print(df_fluor)
# filter the dataframes
df_sequence_no_duplicates, df_mutant_no_duplicates, df_fluor_labeled = filterDataframes(df_fluor, df_sequence, df_mutant, cols_to_add)
df_sequence_no_duplicates.to_csv(f'{outputDir}/sequence_fluor_energy_data.csv', index=False)
df_mutant_no_duplicates.to_csv(f'{outputDir}/mutant_fluor_energy_data.csv', index=False)
df_sequence_no_fluor = df_sequence[~df_sequence['Sequence'].isin(df_sequence_no_duplicates['Sequence'])]
df_mutant_no_fluor = df_mutant[~df_mutant['Mutant'].isin(df_mutant_no_duplicates['Mutant'])]
df_mutant_no_fluor = df_mutant_no_fluor[~df_mutant_no_fluor['Mutant'].isin(df_sequence_no_fluor['Sequence'])]
df_sequence_no_fluor['Type'] = 'WT'
df_mutant_no_fluor['Type'] = 'Mutant'
df_no_fluor = pd.concat([df_sequence_no_fluor, df_mutant_no_fluor])
df_no_fluor['Sample'] = 'none'
# if Region is GAS, then Sample = G
df_no_fluor.loc[df_no_fluor['Region'] == 'GAS', 'Sample'] = 'G'
df_no_fluor.loc[df_no_fluor['Region'] == 'Left', 'Sample'] = 'L'
df_no_fluor.loc[df_no_fluor['Region'] == 'Right', 'Sample'] = 'R'
df_no_fluor = df_no_fluor[~df_no_fluor['Sequence'].isin(df_fluor_labeled['Sequence'])]
df_no_fluor = df_no_fluor.drop_duplicates(subset='Sequence', keep='first')
df_no_fluor['mean_transformed'] = 0
df_sequence_no_fluor.to_csv(f'{outputDir}/sequence_no_fluor.csv', index=False)
df_mutant_no_fluor.to_csv(f'{outputDir}/mutant_no_fluor.csv', index=False)
df_fluor_labeled.to_csv(f'{outputDir}/fluor_WT_mutant_labeled.csv', index=False)
df_no_fluor.to_csv(f'{outputDir}/no_fluor.csv', index=False)
df_all = pd.concat([df_fluor_labeled, df_no_fluor[['Sequence', 'Type', 'Sample', 'mean_transformed']]])
df_all.to_csv(f'{outputDir}/all.csv', index=False)
print(len(df_sequence_no_duplicates))
print(len(df_mutant_no_duplicates))

cols_to_graph = ['Total', 'VDWDiff', 'HBONDDiff', 'IMM1Diff', 'SasaDiff']
#fluor_col = 'Percent GpA'
#error_col = 'Percent Error'
fluor_col = 'mean_transformed'
error_col = 'std_adjusted'
samples = df_sequence_no_duplicates['Sample'].unique()
graphVsFluorescence(df_sequence_no_duplicates, samples, cols_to_graph, fluor_col, error_col, outputDir)
exit(0)

df_mutant_no_duplicates.to_csv(f'{outputDir}/mutant_fluor.csv', index=False)
df_sequence_no_duplicates.to_csv(f'{outputDir}/sequence_fluor.csv', index=False)

# get the WT sequences that have mutants in the dataframe
df_sequences_with_mutant = df_sequence_no_duplicates[df_sequence_no_duplicates['Sequence'].isin(df_mutant_no_duplicates['Sequence'])]
df_mutants_with_WT = df_mutant_no_duplicates[df_mutant_no_duplicates['Sequence'].isin(df_sequence_no_duplicates['Sequence'])]

print(len(df_sequences_with_mutant['Sequence'].unique()))
print(len(df_mutants_with_WT))
exit(0)



output_df = getSequencesWithFluorescenceHigherThanMutant(df_sequences_with_mutant, df_mutants_with_WT, fluor_col) 
print(f'Number of sequences with fluorescence higher than mutant: {len(output_df)}')
print(len(output_df[output_df['Sample'] == 'G']['Sequence']))
cols_to_graph = ['Total', 'VDWDiff', 'HBONDDiff', 'IMM1Diff', 'SasaDiff']
#graphFluorescence(output_df, 'allGasRight', 'Total', outputDir)
graphVsFluorescence(output_df, samples, cols_to_graph, fluor_col, error_col, outputDir)

# all data figures
#graphVsFluorescence(df_mutant_no_duplicates, samples, 'SasaPercDifference', outputDir)

number_seq_in_mutant = len(df_mutant_no_duplicates['Sequence'].unique())
# sequences with mutants data
#graphWTVsFluorescence(df_mutants_with_WT, samples, 'SasaPercDifference', outputDir)
#for sample in samples:
#    df_sample = df_sequence_with_mutant.copy()
#    df_sample = df_sample[df_sample['Sample'] == sample]

print(f'Number of sequences in mutant file: {number_seq_in_mutant}')
# I think the next thing to do is to figure out how I can keep more of these sequences instead of just filtering by all mutants. Is there some metric I can use?
# then after that I think I want to start comparing sequences and mutations 