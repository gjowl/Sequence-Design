import os, sys, pandas as pd

# read in the command line arguments
dataFile = sys.argv[1]
outputDir = sys.argv[2]

# make the output directory
os.makedirs(outputDir, exist_ok=True)

# read in the dataframes
df_data = pd.read_csv(dataFile, sep=',')

# see if the Sequence 1 can be found in Sequence 2
df_data['Potential Homodimer?'] = df_data.apply(lambda row: row['Aligned Seq 1'] in row['Aligned Seq 2'] or row['Aligned Seq 2'] in row['Aligned Seq 1'], axis=1)

# get the matching parts of the sequences
df_data['Matching Sequence'] = df_data.apply(lambda row: row['Aligned Seq 1'] if row['Aligned Seq 1'] in row['Aligned Seq 2'] else row['Aligned Seq 2'], axis=1)

# keep only the rows that are potential homodimers
df_data = df_data[df_data['Potential Homodimer?'] == True]

# get the left dataset
df_left = df_data[df_data['Angle'] > 0]
df_right = df_data[df_data['Angle'] < 0]

# save the dataframes
df_left.to_csv(f'{outputDir}/left.csv', index=False)
df_right.to_csv(f'{outputDir}/right.csv', index=False)