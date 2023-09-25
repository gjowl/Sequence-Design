import os, sys, pandas as pd, numpy as np, matplotlib.pyplot as plt

# read in the command line arguments
sequenceFile = sys.argv[1]
mutantFile = sys.argv[2]
outputDir = sys.argv[3]
wt_fluor_cutoff = float(sys.argv[4])
mutant_fluor_cutoff = float(sys.argv[5])
#percent_wt_cutoff = float(sys.argv[6])

# input variables
if len(sys.argv) < 6:
    # set defaults
    wt_fluor_cutoff = 0.25
    mutant_fluor_cutoff = 0.40
    #percent_wt_cutoff = 50

# make the output directory
os.makedirs(outputDir, exist_ok=True)

# read in the 
df_wt = pd.read_csv(sequenceFile)
df_mut = pd.read_csv(mutantFile)
yAxis = [col for col in df_wt.columns if 'transformed' in col][0]
sort_col = yAxis
sortAscending = True 
numSeqs = 0
output_df = pd.DataFrame()
output_mutant_df = pd.DataFrame()
for sequence in df_wt['Sequence'].unique():
    tmp_wt = df_wt[df_wt['Sequence'] == sequence]
    if len(tmp_wt) > 1:
        tmp_wt = tmp_wt.sort_values(by=[sort_col], ascending=False)
        tmp_wt = tmp_wt.drop_duplicates(subset='Sequence', keep='first')
    df_seq = df_mut[df_mut['Sequence'] == sequence]
    if len(df_seq) < 1:
        continue
    df_seq = df_seq.sort_values(by=[sort_col], ascending=sortAscending)
    bestSequence = df_seq['Mutant'].values[0]
    #df_seq = df_seq[df_seq['Mutant'] == bestSequence]
    # check if the fluorescence of the WT is greater than the mutant
    wt_fluor = tmp_wt[yAxis].values[0]
    if wt_fluor < wt_fluor_cutoff:
        continue
    mutant_fluor = df_seq[yAxis].values[0]
    percentWT = mutant_fluor / wt_fluor * 100
    if mutant_fluor > mutant_fluor_cutoff:
        continue
        #if percentWT > 35:
        #    continue
    numSeqs += 1
    # add the sequence to the output dataframe
    output_df = pd.concat([output_df, tmp_wt], axis=0)
    output_mutant_df = pd.concat([output_mutant_df, df_seq], axis=0)
output_df.to_csv(f'{outputDir}/wt.csv', index=False)
output_mutant_df.to_csv(f'{outputDir}/mutant.csv', index=False)
output_mutant_df['Sequence'] = output_mutant_df['Mutant']
output_df_all = pd.concat([output_df, output_mutant_df], axis=0)
output_df_all.to_csv(f'{outputDir}/all.csv', index=False)
print(numSeqs)

# TODO: add in a way to make multiple types of regression curves