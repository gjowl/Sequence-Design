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

# add 'ILI' to the end of each sequence
df_fluor['Sequence'] = df_fluor['Sequence'].apply(lambda x: x + 'ILI')

df_fluor_seqs = df_fluor[df_fluor['Sequence'].isin(df_sequence['Sequence'])]
df_fluor_mutant = df_fluor[df_fluor['Sequence'].isin(df_mutant['Mutant'])]
print(df_fluor_mutant)

df_sequence = df_sequence[df_sequence['Sequence'].isin(df_fluor_seqs['Sequence'])]
df_mutant = df_mutant[df_mutant['Mutant'].isin(df_fluor_mutant['Sequence'])]
print(df_mutant)

# remove duplicate sequences
df_sequence_no_duplicates = df_sequence.drop_duplicates(subset='Sequence')
df_mutant_no_duplicates = df_mutant.drop_duplicates(subset='Sequence')
df_mutant_no_duplicates.to_csv(f'{outputDir}/mutant_fluor.csv', index=False)
df_sequence_no_duplicates.to_csv(f'{outputDir}/sequence_fluor.csv', index=False)
print(f'Sequences: {df_sequence_no_duplicates.shape[0]}')
print(f'Mutants: {df_mutant_no_duplicates.shape[0]}')