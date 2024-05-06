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
'''

import sys, os, pandas as pd, numpy as np, matplotlib.pyplot as plt, argparse

# initialize the parser
parser = argparse.ArgumentParser(description='Compare the fluorescence of mutants to the WT sequence')

# add the necessary arguments
parser.add_argument('-fluorFile','--fluorescenceFile', type=str, help='the input reconstructed fluorescence csv file')
parser.add_argument('-seqFile','--sequenceFile', type=str, help='the input sequence csv file')
parser.add_argument('-mutFile','--mutantFile', type=str, help='the input mutant csv file')
# add the optional arguments
parser.add_argument('-outDir','--outputDir', type=str, help='the output directory')

# extract the arguments into variables
args = parser.parse_args()
fluorescenceFile = args.fluorescenceFile
sequenceFile = args.sequenceFile
mutantFile = args.mutantFile
# default values for the optional arguments
outputDir = os.getcwd()
# if the optional arguments are not specified, use the default values
if args.outputDir is not None:
    outputDir = args.outputDir
    os.makedirs(outputDir, exist_ok=True)

def filterExperimentDataframes(input_df, percent_error_cutoff, fluor_cutoff, filter_percent_error, filter_fluor):
    output_df = input_df.copy()
    ## filter out by percent error
    if filter_percent_error:
        output_df = output_df[output_df['std_adjusted'] < percent_error_cutoff]
    ## filter out by percent GpA
    if filter_fluor:
        output_df = output_df[output_df['Percent GpA'] < fluor_cutoff]
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
    df_fluor = df_fluor[pd.to_numeric(df_fluor['Segments'], errors='coerce').notnull()].copy()
    # check if ILI is at the end of the sequence; if not, add it
    df_fluor['Sequence'] = df_fluor['Sequence'].apply(lambda x: x if x[-3:] == 'ILI' else x + 'ILI')
    #df_fluor['Sequence'] = df_fluor['Sequence'].apply(lambda x: x + 'ILI')
    # add ILI to the end of the mutant sequences
    #df_mutant['Mutant'] = df_mutant['Mutant'].apply(lambda x: x if x[-3:] == 'ILI' else x + 'ILI')
    #df_mutant['Sequence'] = df_mutant['Sequence'].apply(lambda x: x if x[-3:] == 'ILI' else x + 'ILI')
    #print(df_mutant)
    # get the data for sequences that successfully fluoresce
    df_fluor_seqs = df_fluor[df_fluor['Sequence'].isin(df_sequence['Sequence'])].copy()
    df_fluor_mutant = df_fluor[df_fluor['Sequence'].isin(df_mutant['Mutant'])].copy()
    df_fluor_mutant = df_fluor_mutant[~df_fluor_mutant['Sequence'].isin(df_fluor_seqs['Sequence'])]
    df_fluor_seqs['Type'] = 'WT'
    df_fluor_mutant['Type'] = 'Mutant'
    df_mut = df_mutant.copy()
    df_mut.drop(columns=['Sequence'], inplace=True)
    df_mut.rename(columns={'Mutant': 'Sequence'}, inplace=True)
    df_fluor_mutant = df_fluor_mutant.merge(df_mut[['Sequence', 'Mutant Type']], on='Sequence', how='left')
    df_fluor_mutant = df_fluor_mutant.drop_duplicates(subset='Sequence', keep='first')
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
    df_sequence_no_fluor = df_sequence[~df_sequence['Sequence'].isin(df_sequence_no_duplicates['Sequence'])].copy()
    df_mutant_no_fluor = df_mutant[~df_mutant['Mutant'].isin(df_mutant_no_duplicates['Mutant'])].copy()
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
    #df_no_fluor.loc[df_no_fluor['Region'] == 'GAS', 'Sample'] = 'G'
    #df_no_fluor.loc[df_no_fluor['Region'] == 'Left', 'Sample'] = 'L'
    #df_no_fluor.loc[df_no_fluor['Region'] == 'Right', 'Sample'] = 'R'
    df_no_fluor = df_no_fluor[~df_no_fluor['Sequence'].isin(df_fluor_labeled['Sequence'])]
    df_no_fluor = df_no_fluor.drop_duplicates(subset='Sequence', keep='first')
    df_no_fluor['mean_transformed'] = 0
    return df_sequence_no_fluor, df_mutant_no_fluor, df_no_fluor

# as of 2024-2-15, this file barely does anything other than decreasing the number of columns, renaming columns, and outputting the dataframes
if __name__ == '__main__':
    gpa = 'LIIFGVMAGVIGT'
    g83i = 'LIIFGVMAIVIGT'
    #g83iCutoff = 20000
    
    df_fluor = pd.read_csv(fluorescenceFile)
    df_sequence = pd.read_csv(sequenceFile)
    df_mutant = pd.read_csv(mutantFile)
    
    # THIS CODE IS ANNOYING; FIX IT SO THAT YOU DON'T HAVE TO HARDCODE so much
    # check if wt_seq is a column in the dataframe
    cols_to_add = ['Sequence', 'PercentGpA_transformed', 'std_adjusted', 'Sample', 'Fluorescence', 'FluorStdDev', 'PercentGpA_reconstructed_GpA']
    if 'wt_seq' in df_fluor.columns:
        cols_to_add.append('wt_seq')
    # check if all of the columns are in the dataframe
    if not all([col in df_fluor.columns for col in cols_to_add]):
        # keep only the columns that are in the dataframe
        cols_to_add = [col for col in cols_to_add if col in df_fluor.columns]
    
    # filtering variables
    percent_error_cutoff = 0.30
    fluor_cutoff = 120 # percent GpA
    filter_percent_error = False
    filter_fluor = False 
    transform_col = [col for col in df_fluor.columns if 'transformed' in col][0]
    
    # Filtering
    df_fluor = filterExperimentDataframes(df_fluor, percent_error_cutoff, fluor_cutoff, filter_percent_error, filter_fluor)
    
    # filter the dataframes for duplicates
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