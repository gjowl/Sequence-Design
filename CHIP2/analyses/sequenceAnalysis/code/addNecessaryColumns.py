import os, sys, pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns

# read in the command line arguments
sequenceFile = sys.argv[1]
mutantFile = sys.argv[2]
outputDir = sys.argv[3]

# make the output directory
os.makedirs(outputDir, exist_ok=True)

# read in the input files
df_wt = pd.read_csv(sequenceFile) # wt data file
df_mut = pd.read_csv(mutantFile) # mutant data file

# columns
# check the length of sequence
sequenceLength = len(df_wt['Sequence'].values[0])
if sequenceLength < 21:
    # add LLL and ILI to the sequence
    df_wt['Sequence'] = df_wt.apply(lambda row: 'LLL' + row['Sequence'] + 'ILI', axis=1)
    df_mut['Sequence'] = df_mut.apply(lambda row: 'LLL' + row['Sequence'] + 'ILI', axis=1)

# rename the Sequence column to Mutant for the mutant dataframe
df_mut.rename(columns={'Sequence': 'Mutant'}, inplace=True)
df_mut.rename(columns={'WT Sequence': 'Sequence'}, inplace=True)

# Add the WT_AA column to the mutant dataframe
df_mut['WT_AA'] = df_mut.apply(lambda row: row['Sequence'][row['Position']-1], axis=1)

df_wt.to_csv(f'{outputDir}/wt.csv', index=False)
df_mut.to_csv(f'{outputDir}/mutant.csv', index=False)