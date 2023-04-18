import os, sys, pandas as pd

# read the command line arguments
input_file = sys.argv[1]
output_file = sys.argv[2]
positions = [int (i) for i in sys.argv[3:]]

# read the input file as a dataframe
df = pd.read_csv(input_file, sep=',')

aa = ['G', 'A', 'S']
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

# get the number of rows that have G in each position
total = df.shape[0]
print(f'Total number of sequences: {total}')
for pos in positions:
    print(f'{pos}:')
    print(f'Number of sequences with GAS in position {pos}: {df[df[f"AA{pos}"].isin(aa)].shape[0]}')
    print(f'Number of sequences without GAS in position {pos}: {df[df[f"AA{pos}"] != "G"].shape[0]}')
    # get the number of rows that do not have G in each position
    pos_df = df[df[f'AA{pos}'].isin(aa)]
    for pos2 in positions:
        if pos != pos2:
            print(f'Number of sequences with GAS in position {pos} and without GAS in position {pos2}: {pos_df[~pos_df[f"AA{pos2}"].isin(aa)].shape[0]}')

for pos in positions:
    # get the number of rows that do not have GAS in each position
    print(f'Number of sequences with GAS in position {pos}: {total-df[~df[f"AA{pos}"].isin(aa)].shape[0]}')

# output the dataframe to a csv file without the index
df.to_csv(f'{output_file}_{positions}.csv', index=False)


