import os, sys, pandas as pd

# read the command line arguments
input_file = sys.argv[1]

# get the name of the input file
input_name = input_file.split('/')[-1].split('.')[0]

# define C1 position
C1_pos = 12

# read the input file as a dataframe
df = pd.read_csv(input_file, sep=',', dtype={'Interface': str})

# get the amino acid at the C1 position
df['C1'] = df['Sequence'].str[C1_pos-1]

# remove any sequences where C1 is I
df = df[df['C1'] != 'I']

# remove the C1 column
df = df[[c for c in df.columns if c != 'C1']]

# output the dataframe to a csv file without the index
df.to_csv(f'{input_name}_noC1Mutants.csv', index=False)