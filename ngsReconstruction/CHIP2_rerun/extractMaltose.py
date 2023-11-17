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

tmp_df = pd.DataFrame()
# loop through the unique replicates and write out the dataframes
for replicate in df_maltose['Replicate'].unique():
    # get the current replicate dataframe
    df_rep = df_maltose[df_maltose['Replicate'] == replicate]
    # get the segments with N
    df_nonMaltosePassing = df_rep[df_rep['Segment'].str.contains('N')]
    print(replicate)
    print(df_nonMaltosePassing)
    # get the count of the highest non-maltose segment
    maxCount = df_nonMaltosePassing['Count'].max()
    df_rep = df_rep[df_rep['Count'] >= maxCount]
    tmp_df = pd.concat([tmp_df, df_rep], ignore_index=True)

# write out the final dataframe
tmp_df = tmp_df.drop_duplicates(subset=['Sequence'])
tmp_df.to_csv(f'{outputDir}/maltose_passing.csv', index=False)
