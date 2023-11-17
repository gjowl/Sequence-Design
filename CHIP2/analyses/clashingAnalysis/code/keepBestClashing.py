import os, sys, pandas as pd, numpy as np, matplotlib.pyplot as plt

# read in the command line arguments
sequenceFile = sys.argv[1]
mutantFile = sys.argv[2]
outputDir = sys.argv[3]
mutant_fluor_cutoff = float(sys.argv[4])
percent_wt_cutoff = float(sys.argv[5])
number_of_mutants = int(sys.argv[6])

# input variables
# check if the 4th argument is empty
if len(sys.argv) < 5:
    # set defaults
    wt_fluor_cutoff = 0.35
    mutant_fluor_cutoff = 0.35
    disruptive_mutant_cutoff = 0.5

# make the output directory
os.makedirs(outputDir, exist_ok=True)

# read in the input files 
df_wt = pd.read_csv(sequenceFile) # wt data file
df_mut = pd.read_csv(mutantFile) # mutant data file
yAxis = [col for col in df_wt.columns if 'transformed' in col][0] # get the PercentGpA column
sort_col = yAxis
sortAscending = True 

# setup the output dataframes
output_df = pd.DataFrame()
output_mutant_df = pd.DataFrame()

# loop through the wt sequences 
for sequence in df_wt['Sequence'].unique():
    tmp_wt = df_wt[df_wt['Sequence'] == sequence].copy()
    # get only the best sequence
    if len(tmp_wt) > 1:
        tmp_wt = tmp_wt.sort_values(by=[sort_col], ascending=False)
        tmp_wt = tmp_wt.drop_duplicates(subset='Sequence', keep='first')
    # check if the fluorescence of the WT is greater than the mutant
    wt_fluor = tmp_wt[yAxis].values[0]
    # get the mutants for this sequence and get the lowest energy mutant
    tmp_mut = df_mut[df_mut['Sequence'] == sequence].copy()
    # check if there is are at least two mutants with a lower fluorescence than the WT
    tmp_mut['Fluor Difference'] = wt_fluor - tmp_mut[yAxis]
    # keep the clash mutants only
    clash = tmp_mut[tmp_mut['Mutant Type'].str.contains('clash')]
    #print(wt_fluor)
    #print(tmp_mut[yAxis])
    #print(clash)
    # keep the mutants that are less than the cutoff
    clash = clash[(clash[yAxis] < mutant_fluor_cutoff) | (clash['Fluor Difference'] > percent_wt_cutoff)]
    if len(clash) < number_of_mutants:
        continue # skip if less than the desired number the clash mutants are present
    tmp_mut = tmp_mut.sort_values(by=[sort_col], ascending=sortAscending)
    # get the mutant sequence
    mutant_seq = tmp_mut['Mutant'].values[0]
    # add it to the tmp_wt dataframe
    #tmp_wt['PercentGpA_mutant'] = mutant_fluor 
    #tmp_wt['Fluor Difference'] = wt_mutant_diff
    tmp_wt['Clash Mutant'] = mutant_seq
    wt_seq = tmp_wt['Sequence'].values[0]
    tmp_mut['WT Sequence'] =  wt_seq
    tmp_wt['Mutant Type'] = tmp_mut['Mutant Type'].values[0]
    # add the sequence to the output dataframe
    output_df = pd.concat([output_df, tmp_wt], axis=0)
    output_mutant_df = pd.concat([output_mutant_df, tmp_mut], axis=0)

# add the type column to the output dataframes to distinguish between WT and mutant
output_df['Type'] = 'WT'
output_mutant_df['Type'] = 'Mutant'

# rename the mutant and sequence columns for the output_mutant_df
output_mutant_df = output_mutant_df.rename(columns={'Sequence': 'WTSequence'})
output_mutant_df = output_mutant_df.rename(columns={'Mutant': 'Sequence'})
output_df_all = pd.concat([output_df, output_mutant_df], axis=0)
output_df.to_csv(f'{outputDir}/wt.csv', index=False)
output_mutant_df.to_csv(f'{outputDir}/mutant.csv', index=False)
output_df_all.to_csv(f'{outputDir}/all.csv', index=False)
print(f'Number of WT sequences: {len(output_df)}')