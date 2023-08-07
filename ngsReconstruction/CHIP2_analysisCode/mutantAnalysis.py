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

def graphWTVsFluorescence(input_df, sample_names, energy_col, output_dir):
    # loop through each sample
    for sample in sample_names:
        df_sample = input_df[input_df['Sample'] == sample]
        # plot the WT sequence fluorescence vs the energy
        plt.scatter(df_sample[energy_col], df_sample['mean'])
        # plot the standard deviation
        plt.errorbar(df_sample[energy_col], df_sample['mean'], yerr=df_sample['std'], fmt='o', color='black', ecolor='lightgray', elinewidth=3, capsize=0)
        plt.ylabel('Fluorescence')
        plt.xlabel(energy_col)
        plt.title(f'{energy_col} vs Fluorescence')
        # draw a line of best fit
        m, b = np.polyfit(df_sample[energy_col], df_sample['mean'], 1)
        plt.plot(df_sample[energy_col], m*df_sample[energy_col] + b)
        # add the equation to the plot
        plt.text(0.5, 0.5, f'y = {m:.2f}x + {b:.2f}', horizontalalignment='center', verticalalignment='center', transform=plt.gca().transAxes)
        # calculate the correlation coefficient
        corr = np.corrcoef(df_sample[energy_col], df_sample['mean'])[0,1]
        plt.text(0.5, 0.4, f'r = {corr:.2f}', horizontalalignment='center', verticalalignment='center', transform=plt.gca().transAxes)
        plt.savefig(f'{outputDir}/WT_{sample}_{energy_col}_vs_fluorescence.png')
        plt.clf()

# read in the reconstructed fluorescence dataframe
fluorescenceFile = sys.argv[1]
sequenceFile = sys.argv[2]
mutantFile = sys.argv[3]
outputDir = sys.argv[4]

gpa = 'LIIFGVMAGVIGT'
g83i = 'LIIFGVMAIVIGT'

df_fluor = pd.read_csv(fluorescenceFile)
df_sequence = pd.read_csv(sequenceFile)
df_mutant = pd.read_csv(mutantFile)

#df_controls = df_fluor[df_fluor['Segments'].str.contains('^[A-Z]+$')]
#df_fluor = df_fluor.drop(df_controls.index)
# rid of any segments that are not numerical
df_fluor = df_fluor[pd.to_numeric(df_fluor['Segments'], errors='coerce').notnull()]

# add 'ILI' to the end of each sequence
df_fluor['Sequence'] = df_fluor['Sequence'].apply(lambda x: x + 'ILI')

# get the data for sequences that successfully fluoresce
df_fluor_seqs = df_fluor[df_fluor['Sequence'].isin(df_sequence['Sequence'])]
df_fluor_mutant = df_fluor[df_fluor['Sequence'].isin(df_mutant['Mutant'])]

df_sequence = df_sequence[df_sequence['Sequence'].isin(df_fluor_seqs['Sequence'])]
df_mutant = df_mutant[df_mutant['Mutant'].isin(df_fluor_mutant['Sequence'])]

# remove duplicate sequences
df_sequence_no_duplicates = df_sequence.drop_duplicates(subset='Sequence', keep='first')
df_mutant_no_duplicates = df_mutant.drop_duplicates(subset='Mutant', keep='first')

# add the mean fluorescence to the sequence dataframe
df_sequence_no_duplicates = df_sequence_no_duplicates.merge(df_fluor_seqs[['Sequence', 'mean', 'std', 'Sample']], on='Sequence', how='left')
df_mutant_no_duplicates = df_mutant_no_duplicates.merge(df_fluor_mutant[['Sequence', 'mean', 'std', 'Sample']], left_on='Mutant', right_on='Sequence', how='left')
# The above adds a additional column? get rid of the extra sequence column
df_mutant_no_duplicates = df_mutant_no_duplicates.drop(columns=['Sequence_y'])
# rename the sequence column
df_mutant_no_duplicates = df_mutant_no_duplicates.rename(columns={'Sequence_x': 'Sequence'})

df_mutant_no_duplicates.to_csv(f'{outputDir}/mutant_fluor.csv', index=False)
df_sequence_no_duplicates.to_csv(f'{outputDir}/sequence_fluor.csv', index=False)
df_test = df_fluor.copy()


# check if all sequences are accounted for
# keep sequences not found in df_sequence_no_duplicates
df_test = df_test[~df_test['Sequence'].isin(df_sequence_no_duplicates['Sequence'])]
df_test = df_test[~df_test['Sequence'].isin(df_mutant_no_duplicates['Mutant'])]

# get the WT sequences that have mutants in the dataframe
df_sequences_with_mutant = df_sequence_no_duplicates[df_sequence_no_duplicates['Sequence'].isin(df_mutant_no_duplicates['Sequence'])]
df_mutants_with_WT = df_mutant_no_duplicates[df_mutant_no_duplicates['Sequence'].isin(df_sequence_no_duplicates['Sequence'])]
print(df_sequences_with_mutant.shape)
print(df_mutants_with_WT.shape)


samples = df_sequence_no_duplicates['Sample'].unique()




    


# all data figures
#graphWTVsFluorescence(df_sequence_no_duplicates, samples, 'Total', outputDir)
#graphWTVsFluorescence(df_sequence_no_duplicates, samples, 'VDWDiff', outputDir)
#graphWTVsFluorescence(df_sequence_no_duplicates, samples, 'HBONDDiff', outputDir)
#graphWTVsFluorescence(df_sequence_no_duplicates, samples, 'IMM1Diff', outputDir)
#graphWTVsFluorescence(df_sequence_no_duplicates, samples, 'SasaDiff', outputDir)
#graphWTVsFluorescence(df_mutant_no_duplicates, samples, 'SasaPercDifference', outputDir)

number_seq_in_mutant = len(df_mutant_no_duplicates['Sequence'].unique())
# sequences with mutants data
graphWTVsFluorescence(df_sequences_with_mutant, samples, 'Total', outputDir)
graphWTVsFluorescence(df_sequences_with_mutant, samples, 'VDWDiff', outputDir)
graphWTVsFluorescence(df_sequences_with_mutant, samples, 'HBONDDiff', outputDir)
graphWTVsFluorescence(df_sequences_with_mutant, samples, 'IMM1Diff', outputDir)
graphWTVsFluorescence(df_sequences_with_mutant, samples, 'SasaDiff', outputDir)
graphWTVsFluorescence(df_mutants_with_WT, samples, 'SasaPercDifference', outputDir)
#for sample in samples:
#    df_sample = df_sequence_with_mutant.copy()
#    df_sample = df_sample[df_sample['Sample'] == sample]

print(f'Number of sequences in mutant file: {number_seq_in_mutant}')