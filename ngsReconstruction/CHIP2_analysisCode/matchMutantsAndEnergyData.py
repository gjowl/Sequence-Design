import os, sys, pandas as pd, numpy as np, matplotlib.pyplot as plt

# read in the command line arguments
sequenceFile = sys.argv[1]
energyFile = sys.argv[2]
outputDir = sys.argv[3]

# make the output directory
os.makedirs(outputDir, exist_ok=True)

# read in the input files as dataframes
df_sequence = pd.read_csv(sequenceFile)
df_energy = pd.read_csv(energyFile)

#cols = ['PercentGpA_transformed', 'std_adjusted', 'Sample', 'LB-12H_M9-36H', 'Fluorescence', 'Percent GpA']
cols = ['Mutant', 'PercentGpA_transformed', 'std_adjusted', 'Sample', 'Percent GpA', 'wt_seq']

# loop through each sequence
output_df = pd.DataFrame()
seqs = 0
for sequence in df_sequence['Mutant'].unique():
    # get the dataframe for this sequence
    df_tmp = df_energy[df_energy['Mutant'] == sequence]
    if len(df_tmp) == 0:
        seqs += 1
    # add the cols from the sequence dataframe
    df_tmp = df_tmp.merge(df_sequence[df_sequence['Mutant'] == sequence][cols], on='Mutant', how='left')
    output_df = pd.concat([output_df, df_tmp], axis=0)
print(f'{seqs} sequences not found in the energy file')
output_df.to_csv(f'{outputDir}/mutant_energies.csv', index=False)
