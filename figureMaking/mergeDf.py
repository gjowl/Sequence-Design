import os, sys, pandas as pd

# read the command line arguments
file_to_merge = sys.argv[1]
input_file = sys.argv[2]
output_file = sys.argv[3]

# read the input file and the file to merge as dataframes
df = pd.read_csv(input_file, sep=',', dtype={'Interface': str})
df_to_merge = pd.read_csv(file_to_merge, sep=',', dtype={'Interface': str, 'replicateNumber': str})

# keep only the data with matching mutants
df = df[df['Mutant'].isin(df_to_merge['Mutant'])]

# output the dataframe to a csv file without the index
df.to_csv(f'{output_file}.csv', index=False)