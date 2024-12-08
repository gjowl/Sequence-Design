import os, sys, pandas as pd

def mutateSequence(sequence, position, replacement):
    # mutate the sequence
    mutant_sequence = sequence[:position] + replacement + sequence[position + 1:]
    return mutant_sequence

# read the command line arguments
input_file = sys.argv[1]

# get the name of the input file
input_name = input_file.split('/')[-1].split('.')[0]

# read the input file as a dataframe
df = pd.read_csv(input_file, sep=',', dtype={'Interface': str})

# remove any columns that contain 'AA'
df = df[[c for c in df.columns if 'AA' not in c]]

# shift positions
pos = [4, 5, 8, 9, 12, 13, 16, 17]
aas = ['G', 'A', 'S']
mutant_AAs = ['I', 'L', 'F']
# get the positions to check
for p in pos:
    # get the aa at the positions in the sequence
    df[f'AA{p}'] = df['Sequence'].str[p-1]

# make a duplicate sequence column
df['WTSequence'] = df['Sequence']

# remove any rows that have at least 2 of the aas in the following positions
pos0 = [4, 8]
pos1 = [8, 12]
pos2 = [12, 16]
pos3 = [5, 9]
pos4 = [9, 13]
pos5 = [13, 17]
pos_list = [pos0, pos1, pos2, pos3, pos4, pos5]

for aa in mutant_AAs:
    # initialize the dataframe
    output_df = pd.DataFrame()
    for pos in pos_list:
        # check if AAs are in the positions
        multi_pos_df = df[df[[f'AA{p}' for p in pos]].isin(aas).sum(axis=1).ge(2)]
        # loop through the positions
        for p in pos:
            pos_df = multi_pos_df[multi_pos_df[f'AA{p}'].isin(aas)]
            pos_df[f'Sequence'] = pos_df['Sequence'].apply(lambda x: mutateSequence(x, p-1, aa))
            output_df = pd.concat([output_df, pos_df])
    # rid of any duplicate sequences
    output_df = output_df.drop_duplicates(subset=['Sequence'], keep='first')
    # move the WTSequence column to the front
    output_df = output_df[['WTSequence'] + [c for c in output_df.columns if c != 'WTSequence']]
    # sort by the WTSequence
    output_df = output_df.sort_values(by=['WTSequence'])
    # remove any columns that contain 'AA'
    output_df = output_df[[c for c in output_df.columns if 'AA' not in c]]
    # output the dataframe to a csv file without the index
    output_df.to_csv(f'{input_name}_{aa}_mutants.csv', index=False)