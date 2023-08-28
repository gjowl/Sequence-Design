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
clash = True
sortAscending = False 
yAxis = [col for col in df_wt.columns if 'transformed' in col][0]
fluor_cutoff = 0.35
numSeqs = 0
output_df = pd.DataFrame()
output_mutant_df = pd.DataFrame()
for sequence in df_wt['Sequence'].unique():
    tmp_wt = df_wt[df_wt['Sequence'] == sequence]
    df_seq = df_mut[df_mut['Sequence'] == sequence]
    if len(df_seq) < 2:
        continue
    # get the mutant with the largest SasaPercentDifference
    if clash:
        df_seq = df_seq.sort_values(by=['CHARMM_VDW'], ascending=sortAscending)
    else:
        df_seq = df_seq.sort_values(by=['DimerSasaDifference'], ascending=sortAscending)
    bestSequence = df_seq['Mutant'].values[0]
    df_seq = df_seq[df_seq['Mutant'] == bestSequence]
    # check if the fluorescence of the WT is greater than the mutant
    wt_fluor = tmp_wt[yAxis].values[0]
    if wt_fluor < fluor_cutoff:
        continue
    mutant_fluor = df_seq[yAxis].values[0]
    if mutant_fluor > fluor_cutoff:
        continue
    percentWT = mutant_fluor / wt_fluor * 100
    if percentWT < 50:
        numSeqs += 1
        # add the sequence to the output dataframe
        output_df = pd.concat([output_df, tmp_wt], axis=0)
        output_mutant_df = pd.concat([output_mutant_df, df_seq], axis=0)
output_df.to_csv(f'{outputDir}/wtGreaterThanMutant.csv', index=False)
output_mutant_df.to_csv(f'{outputDir}/wtGreaterThanMutant_mutant.csv', index=False)


# TODO: make a main code of this and the graphing code so that it's streamlined a bit quicker; define some variables to make it easier to change in a config and run multiple times
print(numSeqs)