import os, sys, pandas as pd, numpy as np, matplotlib.pyplot as plt

# read in the command line arguments
sequenceFile = sys.argv[1]
mutantFile = sys.argv[2]
outputDir = sys.argv[3]

# make the output directory
os.makedirs(outputDir, exist_ok=True)

# read in the 
df_wt = pd.read_csv(sequenceFile)
df_mut = pd.read_csv(mutantFile)
clash = False
sortAscending = False 

numSeqs = 0
output_df = pd.DataFrame()
output_mutant_df = pd.DataFrame()
for sequence in df_wt['Sequence'].unique():
    tmp_wt = df_wt[df_wt['Sequence'] == sequence]
    df_seq = df_mut[df_mut['Sequence'] == sequence]
    if len(df_seq) == 0:
        continue
    # get the mutant with the largest SasaPercentDifference
    if clash:
        df_seq = df_seq.sort_values(by=['SasaPercDifference'], ascending=sortAscending)
    else:
        df_seq = df_seq.sort_values(by=['DimerSasaDifference'], ascending=sortAscending)
    bestSequence = df_seq['Mutant'].values[0]
    df_seq = df_seq[df_seq['Mutant'] == bestSequence]
    # check if the fluorescence of the WT is greater than the mutant
    wt_fluor = tmp_wt['mean_transformed'].values[0]
    mutant_fluor = df_seq['mean_transformed'].values[0]
    if wt_fluor > mutant_fluor:
        numSeqs += 1
        # add the sequence to the output dataframe
        output_df = pd.concat([output_df, tmp_wt], axis=0)
        output_mutant_df = pd.concat([output_mutant_df, df_seq], axis=0)
output_df.to_csv(f'{outputDir}/wtGreaterThanMutant.csv', index=False)
output_mutant_df.to_csv(f'{outputDir}/wtGreaterThanMutant_mutant.csv', index=False)

# 
print(numSeqs)