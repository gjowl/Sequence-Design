import os, sys, pandas as pd

# read the command line arguments
file_to_merge = sys.argv[1]
input_file = sys.argv[2]
output_file = sys.argv[3]
output_dir = sys.argv[4]

os.makedirs(name=output_dir, exist_ok=True)

# read the input file and the file to merge as dataframes
df = pd.read_csv(input_file, sep=',', dtype={'Interface': str})
df_to_merge = pd.read_csv(file_to_merge, sep=',', dtype={'Interface': str, 'replicateNumber': str})

# rename the Directory and replicateNumber columns
df.rename(columns={'Directory': 'Optimized_Directory', 'replicateNumber': 'Optimized_replicateNumber', 'Total': 'Optimized_Total'}, inplace=True)

# keep only the 3 to 17 str in the Sequence column
df_to_merge['Sequence'] = df_to_merge['Sequence'].str[3:18]
cols_to_keep = ['Sequence', 'Design', 'replicateNumber', 'Directory', 'Total', 'VDWDiff', 'HBONDDiff', 'IMM1Diff','VDWRepackDiff', 'HBONDRepackDiff', 'IMM1RepackDiff']
# merge that data with the data to merge
df = pd.merge(df, df_to_merge[cols_to_keep], on='Sequence', how='left')
#df = df[df['PercentGpA'] > 0.5]

# keep only the rows where the replicateNumber is not null
df = df[df['replicateNumber'].notnull()]

# add LLL to the beginning of the sequence and ILI to the end of the sequence
df['Sequence'] = 'LLL' + df['Sequence'] + 'ILI'

# output the dataframe to a csv file without the index
df.to_csv(f'{output_dir}/{output_file}.csv', index=False)