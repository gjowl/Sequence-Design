import os, sys, pandas as pd, numpy as np, matplotlib.pyplot as plt

# read in the command line arguments
sequenceFile = sys.argv[1]
mutantFile = sys.argv[2]
outputDir = sys.argv[3]

# make the output directory
os.makedirs(outputDir, exist_ok=True)

# read in the input files 
df_wt = pd.read_csv(sequenceFile) # wt data file
df_mut = pd.read_csv(mutantFile) # mutant data file

output_df = pd.DataFrame()
for sequence in df_mut['Sequence'].unique():
    # get the percent GpA of the mutant from the wt dataframe
    df_seq = df_wt[df_wt['Sequence'] == sequence]
    if df_seq.shape[0] == 0:
        continue
    percentGpA = df_seq['PercentGpA_transformed'].values[0]
    std = df_seq['std_adjusted'].values[0]
    tmp_mut = df_mut[df_mut['Sequence'] == sequence].copy()
    # add the percent GpA to the mutant dataframe
    tmp_mut['PercentGpA_Design'] = percentGpA
    tmp_mut['PercentGpA_Design_std'] = std
    # put those two columns next to PercentGpA_transformed
    tmp_mut = tmp_mut[['Sequence', 'Mutant', 'Sample', 'PercentGpA_Design', 'PercentGpA_Design_std', 'PercentGpA_transformed', 'std_adjusted', 'Fluorescence', 'FluorStdDev']]
    output_df = pd.concat([output_df, tmp_mut])

# write the output file
output_df.to_csv(f'{outputDir}/mutant_design_fluor.csv', index=False)