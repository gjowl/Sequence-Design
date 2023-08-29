import os, sys, pandas as pd, numpy as np

# read in the command line arguments
sequenceFile = sys.argv[1]
energyFile = sys.argv[2]
outputDir = sys.argv[3]
os.makedirs(outputDir, exist_ok=True)

# read in the input files as dataframes
df_sequence = pd.read_csv(sequenceFile)
df_energy = pd.read_csv(energyFile)

# combine the sequence and mutant dataframes
cols = ['Sequence', 'PercentGpA_transformed', 'std_adjusted', 'Sample', 'wt_seq', 'Type', 'Mutant Type']
df_sequence = df_sequence[cols]
df_sequence['Sequence'] = df_sequence['Sequence'].apply(lambda x: x[3:-3])

# merge the energy data with the sequence data by Sequence
df_merged = df_energy.merge(df_sequence, on='Sequence', how='left')
# rid of anything with a nan in the PercentGpA_transformed column
df_merged = df_merged[~df_merged['PercentGpA_transformed'].isna()]
# convert any value for the difference columns greater than 100 to 100
cols = [col for col in df_merged.columns if 'Diff' in col]
for col in cols:
    df_merged[col] = df_merged[col].apply(lambda x: 100 if x > 100 else x)
df_merged['Total'] = df_merged['Total'].apply(lambda x: 100 if x > 100 else x)
df_merged.to_csv(f'{outputDir}/mergedEnergyAndFluor.csv', index=False)