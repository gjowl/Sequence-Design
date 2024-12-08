import os, sys, pandas as pd
import matplotlib.pyplot as plt

# read the command line arguments
input_file = sys.argv[1]
output_file = sys.argv[2]

# read the input file as a dataframe
df = pd.read_csv(input_file, sep=',', dtype={'Interface': str})

# positions to check for c1 and c5
pos = [12, 16]

# get the positions to check
for p in pos:
    # get the aa at the positions in the sequence
    df[f'AA{p}'] = df['Sequence'].str[p-1]

# cutoff for the total energy
cutoffs = [-35, -20, -5]

# initialize the output dataframe
output_df = pd.DataFrame()

# loop through the cutoffs
for i in range(0, len(cutoffs)):
    if i == 0:
        # get the rows with a total energy less than the cutoff
        cutoff_df = df[df['Total'] < cutoffs[i]]
    else:
        # get the rows with a total energy less than the cutoff
        cutoff_df = df[(df['Total'] < cutoffs[i]) & (df['Total'] >= cutoffs[i-1])]
    pos_df = cutoff_df[cutoff_df[f'AA{pos[0]}'] == "G"]
    print(f'# sequences w/ G in position {pos[0]}: {pos_df.shape[0]}')
    # get the number of rows that do not have G in each position
    if i < len(cutoffs) - 1:
        # get the df with G in pos and no S in pos2
        noS_df = pos_df[pos_df[f"AA{pos[1]}"] != "S"]
        print(f'# sequences w/ G in position {pos[0]} and no S in position {pos[1]}: {pos_df[pos_df[f"AA{pos[1]}"] != "S"].shape[0]}')
        print(i)
        if i == 1:
            # remove 20 sequences from the noS_df with the highest total energy
            noS_df = noS_df.sort_values(by=['Total'], ascending=False)
            noS_df = noS_df.iloc[70:]
            print(noS_df['Total'])
        output_df = pd.concat([output_df, noS_df])
    else:
        # randomly choose sequences up to 500
        numSeqs = 430-output_df.shape[0]
        pos_df = pos_df.sample(n=numSeqs, random_state=1)
        output_df = pd.concat([output_df, pos_df])

# sort the output dataframe
output_df = output_df.sort_values(by=['Total'])

# output the dataframe to a csv file without the index
output_df.to_csv(f'{output_file}.csv', index=False)


