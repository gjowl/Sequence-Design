import os, sys, pandas as pd


# read the command line arguments
input_file = sys.argv[1]

# get the name of the input file
input_name = input_file.split('/')[-1].split('.')[0]

# read the input file as a dataframe
df = pd.read_csv(input_file, sep=',')

# remove any columns that contain 'AA'
df = df[[c for c in df.columns if 'AA' not in c]]

# shift positions
pos = [4, 5, 8, 9, 13, 17]
aas = ['G', 'A', 'S']
# get the positions to check
for p in pos:
    # get the aa at the positions in the sequence
    df[f'AA{p}'] = df['Sequence'].str[p-1]

# remove any rows that have at least 2 of the aas
#pos0 = [4, 8]
#pos1 = [5, 9]
pos2 = [9, 13]
pos3 = [13, 17]
#df = df[~df[[f'AA{p}' for p in pos0]].isin(aas).sum(axis=1).ge(2)]
#df = df[~df[[f'AA{p}' for p in pos1]].isin(aas).sum(axis=1).ge(2)]
df = df[~df[[f'AA{p}' for p in pos2]].isin(aas).sum(axis=1).ge(2)]
df = df[~df[[f'AA{p}' for p in pos3]].isin(aas).sum(axis=1).ge(2)]

# output the dataframe to a csv file without the index
df.to_csv(f'{input_name}_noShifts.csv', index=False)