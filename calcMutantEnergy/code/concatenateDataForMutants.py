import os, sys, pandas as pd

# read the command line arguments
input_file = sys.argv[1]
data_file = sys.argv[2]
output_file = sys.argv[3]

# read the input file as a dataframe
df = pd.read_csv(input_file, sep=',')
# read the data file as a dataframe
data_df = pd.read_csv(data_file, sep=',')

# merge the dataframes by the Mutant column and remove any columns that are duplicated
df = pd.merge(df, data_df[['Mutant', 'Region', 'Interface']], on='Mutant')

# output the dataframe to a csv file without the index
df.to_csv(output_file, index=False)