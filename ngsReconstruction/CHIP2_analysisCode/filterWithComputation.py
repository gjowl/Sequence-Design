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

def filterExperimentDataframes(input_df, maltose_col, maltose_cutoff, maltose_limit, 
 filter_maltose, filter_percent_error, filter_fluor):
    output_df = input_df.copy()
    ## filter out by maltose
    if filter_maltose:
        output_df = output_df[output_df[maltose_col] > maltose_cutoff]
        output_df = output_df[output_df[maltose_col] < maltose_limit]
    ## filter out by percent error
    if filter_percent_error:
        percent_error_cutoff = 15
        output_df = output_df[output_df['Percent Error'] < percent_error_cutoff]
    ## filter out by percent GpA
    if filter_fluor:
        percent_GpA_cutoff = 120
        output_df = output_df[output_df['Percent GpA'] < percent_GpA_cutoff]
    return output_df


def mergeDataframes(df_fluor_seqs, df_fluor_mutant, df_sequence_no_duplicates, df_mutant_no_duplicates, cols_to_add):
    output_df_sequence = df_sequence_no_duplicates.copy()
    output_df_mutant = df_mutant_no_duplicates.copy()
    # add the mean fluorescence to the sequence dataframe
    output_df_sequence = output_df_sequence.merge(df_fluor_seqs[cols_to_add], on='Sequence', how='left')
    output_df_mutant = output_df_mutant.merge(df_fluor_mutant[cols_to_add], left_on='Mutant', right_on='Sequence', how='left')
    # The above adds a additional column? get rid of the extra sequence column
    output_df_mutant = output_df_mutant.drop(columns=['Sequence_y'])
    # rename the sequence column
    output_df_mutant = output_df_mutant.rename(columns={'Sequence_x': 'Sequence'})
    return output_df_sequence, output_df_mutant

def filterComputationDataframes(df_fluor, df_sequence, df_mutant, cols_to_add):
    # rid of any segments that are not numerical (removes control sequences)
    df_fluor = df_fluor[pd.to_numeric(df_fluor['Segments'], errors='coerce').notnull()]
    # check if ILI is at the end of the sequence; if not, add it
    df_fluor['Sequence'] = df_fluor['Sequence'].apply(lambda x: x if x[-3:] == 'ILI' else x + 'ILI')
    #df_fluor['Sequence'] = df_fluor['Sequence'].apply(lambda x: x + 'ILI')
    # get the data for sequences that successfully fluoresce
    df_fluor_seqs = df_fluor[df_fluor['Sequence'].isin(df_sequence['Sequence'])]
    df_fluor_mutant = df_fluor[df_fluor['Sequence'].isin(df_mutant['Mutant'])]
    df_fluor_mutant = df_fluor_mutant[~df_fluor_mutant['Sequence'].isin(df_fluor_seqs['Sequence'])]
    df_fluor_seqs['Type'] = 'WT'
    df_fluor_mutant['Type'] = 'Mutant'
    df_mut = df_mutant.copy()
    df_mut.drop(columns=['Sequence'], inplace=True)
    df_mut.rename(columns={'Mutant': 'Sequence'}, inplace=True)
    df_fluor_mutant = df_fluor_mutant.merge(df_mut[['Sequence', 'Mutant Type']], on='Sequence', how='left')
    df_fluor_mutant = df_fluor_mutant.drop_duplicates(subset='Sequence', keep='first')
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

def getNonFluorescentSequences(df_sequence, df_mutant, df_sequence_no_duplicates, df_mutant_no_duplicates, df_fluor_labeled):
    df_sequence_no_fluor = df_sequence[~df_sequence['Sequence'].isin(df_sequence_no_duplicates['Sequence'])]
    df_mutant_no_fluor = df_mutant[~df_mutant['Mutant'].isin(df_mutant_no_duplicates['Mutant'])]
    df_mutant_no_fluor = df_mutant_no_fluor[~df_mutant_no_fluor['Mutant'].isin(df_sequence_no_fluor['Sequence'])]
    df_sequence_no_fluor['Type'] = 'WT'
    df_mutant_no_fluor['Type'] = 'Mutant'
    # get mutant type from the mutant dataframe
    df_mutant_no_fluor = df_mutant_no_fluor.merge(df_mutant[['Mutant', 'Mutant Type']], on='Mutant', how='left')
    df_mutant_no_fluor = df_mutant_no_fluor.rename(columns={'Mutant Type': 'Type'})
    df_mutant_no_fluor = df_mutant_no_fluor.drop_duplicates(subset='Mutant', keep='first')
    df_no_fluor = pd.concat([df_sequence_no_fluor, df_mutant_no_fluor])
    df_no_fluor['Sample'] = 'none'
    # if Region is GAS, then Sample = G
    df_no_fluor.loc[df_no_fluor['Region'] == 'GAS', 'Sample'] = 'G'
    df_no_fluor.loc[df_no_fluor['Region'] == 'Left', 'Sample'] = 'L'
    df_no_fluor.loc[df_no_fluor['Region'] == 'Right', 'Sample'] = 'R'
    df_no_fluor = df_no_fluor[~df_no_fluor['Sequence'].isin(df_fluor_labeled['Sequence'])]
    df_no_fluor = df_no_fluor.drop_duplicates(subset='Sequence', keep='first')
    df_no_fluor['mean_transformed'] = 0
    return df_sequence_no_fluor, df_mutant_no_fluor, df_no_fluor

# TODO: currently comparing energies between L designs and A designs; fix
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
cols_to_add = ['Sequence', 'mean_transformed', 'std_adjusted', 'Sample', 'wt_seq']
#cols_to_add = ['Sequence', 'Percent GpA', 'Percent Error', 'Sample']

# filtering variables
maltose_col = 'LB-12H_M9-36H'
maltose_cutoff = -97
maltose_limit = 10000000
percent_error_cutoff = 15
fluor_cutoff = 120 # percent GpA
filter_maltose = False
filter_percent_error= True
filter_fluor = False 

# Filtering
df_fluor = filterExperimentDataframes(df_fluor, maltose_col, maltose_cutoff, maltose_limit, filter_maltose, filter_percent_error, filter_fluor)

# get the error for each sequence
df_fluor['std_adjusted'] = df_fluor['mean_transformed'] * df_fluor['Percent Error'] / 100

# filter the dataframes
df_sequence_no_duplicates, df_mutant_no_duplicates, df_fluor_labeled = filterComputationDataframes(df_fluor, df_sequence, df_mutant, cols_to_add)

# get sequences that don't fluoresce
df_sequence_no_fluor, df_mutant_no_fluor, df_no_fluor = getNonFluorescentSequences(df_sequence, df_mutant, df_sequence_no_duplicates, df_mutant_no_duplicates, df_fluor_labeled)

# output dataframes
df_sequence_no_duplicates.to_csv(f'{outputDir}/sequence_fluor_energy_data.csv', index=False)
df_mutant_no_duplicates.to_csv(f'{outputDir}/mutant_fluor_energy_data.csv', index=False)
df_sequence_no_fluor.to_csv(f'{outputDir}/sequence_no_fluor.csv', index=False)
df_mutant_no_fluor.to_csv(f'{outputDir}/mutant_no_fluor.csv', index=False)
df_fluor_labeled.to_csv(f'{outputDir}/fluor_WT_mutant_labeled.csv', index=False)
df_no_fluor.to_csv(f'{outputDir}/no_fluor.csv', index=False)
df_all = pd.concat([df_fluor_labeled, df_no_fluor[['Sequence', 'Type', 'Sample', 'mean_transformed']]])
df_all.to_csv(f'{outputDir}/all.csv', index=False)
print(f'Sequences: {len(df_sequence_no_duplicates)}')
print(f'Mutants: {len(df_mutant_no_duplicates)}')
#exit(0)

## get the WT sequences that have mutants in the dataframe
#df_sequences_with_mutant = df_sequence_no_duplicates[df_sequence_no_duplicates['Sequence'].isin(df_mutant_no_duplicates['Sequence'])]
#df_mutants_with_WT = df_mutant_no_duplicates[df_mutant_no_duplicates['Sequence'].isin(df_sequence_no_duplicates['Sequence'])]
#exit(0)