import os, sys, pandas as pd, matplotlib.pyplot as plt, numpy as np

# read command line arguments
sequenceFile = sys.argv[1]
energyFile = sys.argv[2]
outputDir = sys.argv[3]
os.makedirs(outputDir, exist_ok=True)

# read in the data files
sequence_df = pd.read_csv(sequenceFile)
energy_df = pd.read_csv(energyFile)

# merge the dataframes by sequence
maltose_col = 'LB-12H_M9-36H'
#maltose_cutoff = -99
#maltose_limit = 99999900
#sequence_df = sequence_df[sequence_df[maltose_col] > maltose_cutoff]
#sequence_df = sequence_df[sequence_df[maltose_col] < maltose_limit]
cols = ['Sequence', 'PercentGpA', 'PercentStd', 'Type', 'Clash Mutant', 'Mutant Type', 'Position', 'Disruptive Mutant', 'PercentGpA_mutant', 'WT Sequence', 'Fluor Difference'] #TODO add more to carry over including the diffs; which for some reason are getting calcd again?
# check if all the columns are present, otherwise only keep the ones that are present
if all(col in sequence_df.columns for col in cols):
    sequence_df = sequence_df[cols]
else:
    # get the columns that are present
    cols = [col for col in cols if col in sequence_df.columns]
    sequence_df = sequence_df[cols]
sequence_df['Sequence'] = sequence_df['Sequence'].apply(lambda x: x[3:-3])
energy_df['Sequence'] = energy_df['Directory'].apply(lambda x: x[3:-3])
df = sequence_df.merge(energy_df, on='Sequence', how='left')
#df.rename(columns={'PercentGpA_transformed': 'PercentGpA', 'std_adjusted': 'PercentStd'}, inplace=True)
df.to_csv(f'{outputDir}/mergedData.csv', index=False)

execPlot = f'python3 code/analyzeData.py {outputDir}/mergedData.csv {outputDir}'
os.system(execPlot)