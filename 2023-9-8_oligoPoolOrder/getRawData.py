import os, sys, pandas as pd

# read in the command line arguments
sequenceFile = sys.argv[1]
dataFile = sys.argv[2]

# read in the input files
df_seq = pd.read_csv(sequenceFile)
df_data = pd.read_csv(dataFile)

# add ILI to the sequence column
df_seq['Sequence'] = df_seq['Sequence'] + 'ILI'

# find sequences in the sequence file and keep that data from the datafile
df_data = df_data[df_data['Sequence'].isin(df_seq['Sequence'])]

# output the data
df_data.to_csv(f'{dataFile[:-4]}_order.csv', index=False)