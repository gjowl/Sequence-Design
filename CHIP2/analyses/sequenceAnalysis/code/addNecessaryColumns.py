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

#df_wt['Position'] = df_wt.apply(i for i in xrange(1, len(df_wt['Sequence'])+1) if df_wt['Sequence'][i] != df_wt['Disruptive Mutant'][i], axis=1)
# get the position of the mutation between the sequence column and disruptive mutant column
df_wt['Position'] = df_wt.apply(lambda row: [i for i in range(1, len(row['Sequence'])+1) if row['Sequence'][i-1] != row['Disruptive Mutant'][i-1]][0], axis=1)
df_wt['Position'] = df_wt['Position'].astype(int)-1 # subtract 1 to the position to account for starting at 0

# Add the WT_AA column to the mutant dataframe
df_wt['WT_AA'] = df_wt.apply(lambda row: row['Sequence'][row['Position']], axis=1)
df_mut['WT_AA'] = df_mut.apply(lambda row: row['Sequence'][row['Position']], axis=1)

# add the mutAA column to the mutant dataframe
df_mut['mut_AA'] = df_mut.apply(lambda row: row['Mutant'][row['Position']], axis=1)
df_wt['mut_AA'] = df_wt.apply(lambda row: row['Disruptive Mutant'][row['Position']], axis=1)

df_wt.to_csv(f'{outputDir}/wt.csv', index=False)
df_mut.to_csv(f'{outputDir}/mutant.csv', index=False)

# combine the files with the given columns
cols = ['Sample', 'Sequence', 'Position', 'Type', 'Mutant Type', 'WT_AA', 'mut_AA', 'PercentGpA', 'PercentStd']
df_wt = df_wt[cols] 
df_mut = df_mut[cols]
df_all = pd.concat([df_wt, df_mut])
df_all.to_csv(f'{outputDir}/all.csv', index=False)
