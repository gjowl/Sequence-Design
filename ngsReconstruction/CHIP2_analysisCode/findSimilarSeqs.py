import sys, os, pandas as pd, numpy as np, matplotlib.pyplot as plt

def match(s1, s2):
    num_diff = 0
    for i, (c1, c2) in enumerate(zip(s1, s2)):
        if c1 != c2:
            num_diff += 1
    return num_diff 

def getSimilarSequenceDataframe(input_df, samples):
    output_df = pd.DataFrame()
    samples = df_fluor['Sample'].unique()
    for sample in samples:
        df_sample = df_fluor[df_fluor['Sample'] == sample]
        # loop through all of the sequences
        for seq in df_sample['Sequence'].unique():
            matching_sequences = [seq]
            for seq2  in df_sample['Sequence'].unique():
                if match(seq, seq2) < 2:
                    matching_sequences.append(seq2)
            # keep only the unique sequences
            matching_sequences = list(set(matching_sequences))
            if len(matching_sequences) > 3:
                # add that data to the dataframe
                df_matching = df_sample.copy()
                df_matching = df_matching[df_matching['Sequence'].isin(matching_sequences)]
                df_matching['WT_Sequence'] = seq
                output_df = pd.concat([output_df, df_matching])
        # remove duplicates
        output_df = output_df.drop_duplicates()
        #print(len(output_df))
        #print(len(output_df[output_df['Type'] == 'Mutant']))
        #print(len(output_df[output_df['Type'] == 'WT']))
        #print(len(output_df['WT_Sequence'].unique()))
    return output_df

def calculatePercentDifference(input_df, wt_seq):
    df_wt = input_df.copy()
    # calculate the percent difference between the mutant and the WT
    wt_percent = input_df[input_df['Sequence'] == wt_seq]['Percent GpA'].values[0]
    df_wt['Percent Difference'] = df_wt['Percent GpA'] - wt_percent
    return df_wt

# read in the input files
fluor_file = sys.argv[1]
output_dir = sys.argv[2]

os.makedirs(output_dir, exist_ok=True)

# read in the dataframes
df_fluor = pd.read_csv(fluor_file)
print(len(df_fluor))

df_fluor_similar = getSimilarSequenceDataframe(df_fluor, df_fluor['Sample'].unique())
print(len(df_fluor_similar))
# I think this is the dataframe of sequences I would want next; now I have to look at the mutants that are gone and see if they are gone for a reason, and compare fluorescence for each
# waht type of figure should I use for mutant comparisons?

output_df = pd.DataFrame()
for wt in df_fluor_similar['WT_Sequence'].unique():
    df_wt = df_fluor_similar[df_fluor_similar['WT_Sequence'] == wt]
    df_wt = calculatePercentDifference(df_wt, wt)
    # check if there are any percent differences that are greater than 10%
    df_wt = df_wt[df_wt['Percent Difference'] > 5]
    if len(df_wt) > 0:
        output_df = pd.concat([output_df, df_wt])

print(len(output_df))
exit(0)