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
df_wt['Position'] = df_wt.apply(lambda row: [i for i in range(1, len(row['Sequence'])+1) if row['Sequence'][i-1] != row['Clash Mutant'][i-1]][0], axis=1)
df_wt['Position'] = df_wt['Position'].astype(int)-1 # subtract 1 to the position to account for starting at 0

# Add the WT_AA column to the mutant dataframe
df_wt['WT_AA'] = df_wt.apply(lambda row: row['Sequence'][row['Position']], axis=1)
df_mut['WT_AA'] = df_mut.apply(lambda row: row['Sequence'][row['Position']], axis=1)

# add the mutAA column to the mutant dataframe
df_mut['mut_AA'] = df_mut.apply(lambda row: row['Mutant'][row['Position']], axis=1)
df_wt['mut_AA'] = df_wt.apply(lambda row: row['Clash Mutant'][row['Position']], axis=1)

df_wt.rename(columns={'Clash Mutant': 'Mutant'}, inplace=True)

# keep only the sequences that are present in the wt dataframe
df_mut = df_mut[df_mut['Sequence'].isin(df_wt['Sequence'].unique())]

df_wt.to_csv(f'{outputDir}/wt.csv', index=False)
df_mut.to_csv(f'{outputDir}/mutant.csv', index=False)

# check if PercentGpA is a column
if 'PercentGpA' not in df_wt.columns:
    df_wt['PercentGpA'] = df_wt['PercentGpA_transformed']
    df_mut['PercentGpA'] = df_mut['PercentGpA_transformed']
if 'PercentStd' not in df_wt.columns:
    df_wt['PercentStd'] = df_wt['std_adjusted']
    df_mut['PercentStd'] = df_mut['std_adjusted']

# combine the files with the given columns
cols = ['Sample', 'Sequence', 'Mutant', 'Position', 'Type', 'Mutant Type', 'WT_AA', 'mut_AA', 'PercentGpA', 'PercentStd']

# add in wt data for each mutant, since the wt data only includes the best clash mutant for each sequence
# change the mutant type to wt
df_copy_wt = df_mut.copy()
df_copy_wt['Type'] = 'WT'
copyCols = ['PercentGpA', 'PercentStd']
# get the values from the wt dataframe for each sequence
df_copy_wt['PercentGpA'] = df_copy_wt.apply(lambda row: df_wt[df_wt['Sequence'] == row['Sequence']]['PercentGpA'].values[0], axis=1)
df_copy_wt['PercentStd'] = df_copy_wt.apply(lambda row: df_wt[df_wt['Sequence'] == row['Sequence']]['PercentStd'].values[0], axis=1)

# output the wt and mutant dataframes
df_copy_wt = df_copy_wt[cols].copy()
df_all = pd.concat([df_wt[cols], df_mut[cols], df_copy_wt[cols]])
df_all.to_csv(f'{outputDir}/all.csv', index=False)

# check if each sequence has at least 1 void and 1 clash in the Mutant Type column
df_mut['Void'] = df_mut['Mutant Type'].apply(lambda x: 'void' in x)
df_mut['Clash'] = df_mut['Mutant Type'].apply(lambda x: 'clash' in x)
df_void = df_mut[df_mut['Void'] == True]
df_clash = df_mut[df_mut['Clash'] == True]

# keep only sequences that are present in both the void and clash dataframes (at least 1 void and 1 clash mutant per sequence)
df_c_v = df_void[df_void['Sequence'].isin(df_clash['Sequence'].unique())]
df_wt_cv = df_wt[df_wt['Sequence'].isin(df_c_v['Sequence'].unique())]
df_mut_cv = df_mut[df_mut['Sequence'].isin(df_c_v['Sequence'].unique())]
df_copy_wt_cv = df_copy_wt[df_copy_wt['Sequence'].isin(df_c_v['Sequence'].unique())]
output_df = pd.concat([df_wt_cv[cols], df_mut_cv[cols], df_copy_wt_cv[cols]])
output_df.to_csv(f'{outputDir}/clash_void.csv', index=False)