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

# merge that data with the data to merge
df = pd.merge(df, df_to_merge[['Sequence', 'replicateNumber', 'Directory']], on='Sequence', how='left')
df = df[df['PercentGpA'] > 0.5]

# output the dataframe to a csv file without the index
df.to_csv(f'{output_dir}/{output_file}.csv', index=False)