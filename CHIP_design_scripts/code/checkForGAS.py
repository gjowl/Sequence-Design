import os, sys, pandas as pd

# read the command line arguments
input_file = sys.argv[1]
output_file = sys.argv[2]
positions = [int (i) for i in sys.argv[3:]]

# read the input file as a dataframe
df = pd.read_csv(input_file, sep=',')

aa = ['G']
#aa = ['G', 'A', 'S']
for pos in positions:
    # get the aa at the positions in the sequence
    df[f'AA{pos}'] = df['Sequence'].str[pos-1]

# combine all columns containing aa into a single column
df['AAs'] = df[[f'AA{pos}' for pos in positions]].apply(lambda x: '|'.join(x), axis=1)

# get the rows where there are at least 2 of the aas
# check how many positions are being checked
if len(positions) > 1:
    df = df[df['AAs'].str.count('|'.join(aa)) >= 2]
else:
    df = df[df['AAs'].str.count('|'.join(aa)) >= 1]
print(df)

# remove the columns containing aa
df = df.drop([f'AA{pos}' for pos in positions], axis=1)
df = df.drop(['AAs'], axis=1)

# output the dataframe to a csv file without the index
df.to_csv(f'{output_file}_{positions}.csv', index=False)


