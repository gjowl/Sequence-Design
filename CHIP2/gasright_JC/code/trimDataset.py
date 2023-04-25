import os, sys, pandas as pd

# read the command line arguments
input_file = sys.argv[1]
output_file = sys.argv[2]

# read the input file as a dataframe
df = pd.read_csv(input_file, sep=',', dtype={'Interface': str})

# remove any duplicate sequences
df = df.drop_duplicates(subset=['Sequence'])

# keep the data within the GASright region
df = df[df['endXShift'] < 7.5]

# output the dataframe to a csv file without the index
df.to_csv(output_file, index=False)
