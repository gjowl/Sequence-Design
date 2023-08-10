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

def graphFluorescence(input_df, output_file, energy_col, output_dir):
    # plot the WT sequence fluorescence vs the energy
    plt.scatter(input_df[energy_col], input_df['mean'])
    # plot the standard deviation
    plt.errorbar(input_df[energy_col], input_df['mean'], yerr=input_df['std'], fmt='o', color='black', ecolor='lightgray', elinewidth=3, capsize=0)
    plt.ylabel('Fluorescence')
    plt.xlabel(energy_col)
    plt.title(f'{energy_col} vs Fluorescence')
    # draw a line of best fit
    m, b = np.polyfit(input_df[energy_col], input_df['mean'], 1)
    plt.plot(input_df[energy_col], m*input_df[energy_col] + b)
    # add the equation to the plot
    plt.text(0.1, 1.12, f'y = {m:.2f}x + {b:.2f}', horizontalalignment='center', verticalalignment='center', transform=plt.gca().transAxes)
    # calculate the correlation coefficient
    corr = np.corrcoef(input_df[energy_col], input_df['mean'])[0,1]
    plt.text(0.1, 1.09, f'r = {corr:.2f}', horizontalalignment='center', verticalalignment='center', transform=plt.gca().transAxes)
    # add the total number of sequences to the plot
    plt.text(0.1, 1.06, f'n = {len(input_df)}', horizontalalignment='center', verticalalignment='center', transform=plt.gca().transAxes)
    plt.savefig(f'{outputDir}/{output_file}.png')
    plt.clf()

def graphWTVsFluorescence(input_df, sample_names, energy_col, output_dir):
    # loop through each sample
    for sample in sample_names:
        df_sample = input_df[input_df['Sample'] == sample]
        graphFluorescence(df_sample, f'{sample}_{energy_col}', energy_col, output_dir)

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

# remove any sequences below G83I
#df_fluor = df_fluor[df_fluor['mean'] > g83iCutoff]

#df_controls = df_fluor[df_fluor['Segments'].str.contains('^[A-Z]+$')]
#df_fluor = df_fluor.drop(df_controls.index)
# rid of any segments that are not numerical
df_fluor = df_fluor[pd.to_numeric(df_fluor['Segments'], errors='coerce').notnull()]
print("start",len(df_fluor[df_fluor['Sample'] == 'G']['Sequence']))

# add 'ILI' to the end of each sequence
df_fluor['Sequence'] = df_fluor['Sequence'].apply(lambda x: x + 'ILI')
print("ili",len(df_fluor[df_fluor['Sample'] == 'G']['Sequence']))

# get the data for sequences that successfully fluoresce
df_fluor_seqs = df_fluor[df_fluor['Sequence'].isin(df_sequence['Sequence'])]
df_fluor_mutant = df_fluor[df_fluor['Sequence'].isin(df_mutant['Mutant'])]
print("fluor G",len(df_fluor_seqs[df_fluor_seqs['Sample'] == 'G']['Sequence']))
print("fluor L",len(df_fluor_seqs[df_fluor_seqs['Sample'] == 'L']['Sequence']))
print("fluor R",len(df_fluor_seqs[df_fluor_seqs['Sample'] == 'R']['Sequence']))
df_fluor_seqs = df_fluor_seqs.merge(df_sequence[['Sequence', 'Total']], on='Sequence')
samples = df_fluor_seqs['Sample'].unique()
graphWTVsFluorescence(df_fluor_seqs, samples, 'Total', outputDir)




df_sequence = df_sequence[df_sequence['Sequence'].isin(df_fluor_seqs['Sequence'])]
df_mutant = df_mutant[df_mutant['Mutant'].isin(df_fluor_mutant['Sequence'])]
print("mut",len(df_sequence[df_sequence['Region'] == 'GAS']['Sequence']))

#print(len(df_sequence[df_sequence['Design'] == 'GJL']['Sequence']))

# remove duplicate sequences
df_sequence_no_duplicates = df_sequence.drop_duplicates(subset='Sequence', keep='first')
df_mutant_no_duplicates = df_mutant.drop_duplicates(subset='Mutant', keep='first')
# TODO: I may be getting rid of mutants that come from multiple sequences; check and fix above if necessary

# add the mean fluorescence to the sequence dataframe
df_sequence_no_duplicates = df_sequence_no_duplicates.merge(df_fluor_seqs[['Sequence', 'mean', 'std', 'Sample', 'Rep1-Fluor', 'Rep2-Fluor', 'Rep3-Fluor']], on='Sequence', how='left')
df_mutant_no_duplicates = df_mutant_no_duplicates.merge(df_fluor_mutant[['Sequence', 'mean', 'std', 'Sample', 'Rep1-Fluor', 'Rep2-Fluor', 'Rep3-Fluor']], left_on='Mutant', right_on='Sequence', how='left')
# The above adds a additional column? get rid of the extra sequence column
df_mutant_no_duplicates = df_mutant_no_duplicates.drop(columns=['Sequence_y'])
# rename the sequence column
df_mutant_no_duplicates = df_mutant_no_duplicates.rename(columns={'Sequence_x': 'Sequence'})
print("fluor G",len(df_sequence_no_duplicates[df_sequence_no_duplicates['Sample'] == 'G']['Sequence']))
print("fluor L",len(df_sequence_no_duplicates[df_sequence_no_duplicates['Sample'] == 'L']['Sequence']))
print("fluor R",len(df_sequence_no_duplicates[df_sequence_no_duplicates['Sample'] == 'R']['Sequence']))

df_mutant_no_duplicates.to_csv(f'{outputDir}/mutant_fluor.csv', index=False)
df_sequence_no_duplicates.to_csv(f'{outputDir}/sequence_fluor.csv', index=False)

print(len(df_sequence_no_duplicates[df_sequence_no_duplicates['Sample'] == 'G']['Sequence']))

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
graphWTVsFluorescence(df_sequence_no_duplicates, samples, 'Total', outputDir)
# get the number of sequences with fluorescence higher than mutant
successfulSeqs = 0
output_df = pd.DataFrame()
for sequence in df_sequences_with_mutant['Sequence']:
    sequenceFluor = df_sequences_with_mutant.loc[df_sequences_with_mutant['Sequence'] == sequence, 'mean'].values[0]
    mutantFluor = df_mutants_with_WT.loc[df_mutants_with_WT['Sequence'] == sequence, 'mean']
    mutantFluor = mutantFluor.divide(sequenceFluor)*100
    if any(mutantFluor.values < 100):
        successfulSeqs += 1
        # add that row to the dataframe
        output_df = pd.concat([output_df, df_sequences_with_mutant[df_sequences_with_mutant['Sequence'] == sequence]], axis=0)

print(f'Number of sequences with fluorescence higher than mutant: {successfulSeqs}')
for sample in output_df['Sample'].unique():
    sample_df = output_df[output_df['Sample'] == sample]
    print(f'Number of sequences with fluorescence higher than mutant in {sample}: {len(sample_df)}')
    #graphFluorescence(sample_df, f'{sample}_higherThanMutant', 'Total', outputDir)
    sample_df.to_csv(f'{outputDir}/{sample}_higherThanMutant.csv', index=False)

exit(0)
#print(len(output_df[output_df['Sample'] == 'G']['Sequence']))
#print(len(output_df[output_df['Sample'] == 'D']['Sequence']))
#d_df = output_df[output_df['Sample'] == 'D']
#g_df = output_df[output_df['Sample'] == 'G']
#d_df.to_csv(f'{outputDir}/D_df.csv', index=False)
#g_df.to_csv(f'{outputDir}/G_df.csv', index=False)
#graphFluorescence(output_df, 'allData', 'Total', outputDir)
graphFluorescence(df_sequences_with_mutant, 'allData', 'Total', outputDir)


#graphWTVsFluorescence(output_df, samples, 'Total', outputDir)
#exit(0)

    


# all data figures
#graphWTVsFluorescence(output_df, samples, 'Total', outputDir)
#graphWTVsFluorescence(output_df, samples, 'VDWDiff', outputDir)
#graphWTVsFluorescence(output_df, samples, 'HBONDDiff', outputDir)
#graphWTVsFluorescence(output_df, samples, 'IMM1Diff', outputDir)
#graphWTVsFluorescence(output_df, samples, 'SasaDiff', outputDir)
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