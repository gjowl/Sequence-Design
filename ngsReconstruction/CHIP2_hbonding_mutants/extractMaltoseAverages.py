import os, sys, pandas as pd

# read in the command line arguments
inputFile = sys.argv[1]
outputDir = sys.argv[2]

# make the output directory
os.makedirs(outputDir, exist_ok=True)

# read in the input file
df = pd.read_csv(inputFile)
# get the maltose data by filtering on the replicate column
df_maltose = df[df['Replicate'].str.contains('maltose')]
df_maltose.to_csv(f'{outputDir}/all_maltose.csv', index=False)

# create sample column for each replicate by the first character of the replicate column
df_maltose['Sample'] = df_maltose['Replicate'].str[0]
tmp_df = pd.DataFrame()
# loop through the unique replicates and write out the dataframes
for sample in df_maltose['Sample'].unique():
    # get the current replicate dataframe
    df_sample = df_maltose[df_maltose['Sample'] == sample]
    # get the average counts for each sequence, keeping the segment column
    df_sample = df_sample.groupby(['Sequence', 'Segment', 'Sample'], as_index=False).mean()
    # get the segments with N
    df_nonMaltosePassing = df_sample[df_sample['Segment'].str.contains('N')]
    print(df_nonMaltosePassing)
    # get the count of the highest non-maltose segment
    maxCount = df_nonMaltosePassing['Percentage'].max()/6
    df_sample = df_sample[df_sample['Percentage'] >= maxCount]
    tmp_df = pd.concat([tmp_df, df_sample], ignore_index=True)
# write out the final dataframe
tmp_df = tmp_df.drop_duplicates(subset=['Sequence'])
tmp_df.to_csv(f'{outputDir}/maltose_passing.csv', index=False)
