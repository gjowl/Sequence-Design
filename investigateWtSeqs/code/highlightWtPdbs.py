import pymol.cmd as cmd
import os, sys, pandas as pd

# list of the alphabet
alphabet = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')

def convertToChainLetter(segment):
    if segment > 26:
        return alphabet[segment % 26 - 1] + alphabet[segment // 26 - 1]
    else:
        return alphabet[segment]

def getChains(df):
    # initialize the output dataframe
    output_df = df.copy()
    # reset the index
    output_df = output_df.reset_index(drop=True)
    chain1_list, chain2_list = [], []
    for index, row in output_df.iterrows():
        # get the segment #s
        segment1 = row['Segment 1 #']
        segment2 = row['Segment 2 #']
        # convert the segment #s to chain letters
        chain1, chain2 = convertToChainLetter(segment1), convertToChainLetter(segment2)
        chain1_list.append(chain1), chain2_list.append(chain2)
    # add the chain letters to the dataframe using concat
    output_df = pd.concat([output_df, pd.DataFrame({'Chain 1': chain1_list, 'Chain 2': chain2_list})], axis=1)
    return output_df 

# read the command line arguments
input_file = sys.argv[1]

# read the input file as a dataframe
df = pd.read_csv(input_file, sep=',')

# loop through the sequences
for pdb in df['PDB Id']:
    # fetch the pdb file
    cmd.fetch(pdb)
    # get the pdb dataframe
    pdb_df = df[df['PDB Id'] == pdb]
    # keep the rows with unique segments
    pdb_df = pdb_df.drop_duplicates(subset=['Segment 1 #', 'Segment 2 #'])
    # loop through the rows
    # get chain letters for the segments
    pdb_df = getChains(pdb_df)
    print(pdb_df)
    # loop through the rows
    for index, row in pdb_df.iterrows():
        # get the chain letters
        chain1, chain2 = row['Chain 1'], row['Chain 2']
        # get the start and end positions
        start1, end1 = row['Seg 1 Pos start #'], row['Seg 1 Pos end #']
        start2, end2 = row['Seg 2 Pos start #'], row['Seg 2 Pos end #']
        # highlight the segments
        cmd.color('red', f'chain {chain1} and resi {start1}-{end1}')
        cmd.color('red', f'chain {chain2} and resi {start2}-{end2}')
        # highlight the interface
        #cmd.color('blue', f'chain {chain1} and chain {chain2} and resi {start}-{end}')
    # save the pse
    cmd.save(f'{pdb}.pse') 
    exit(0)
    # convert segment #s to chain letters by getting the index in the alphabet
    # check if the segment # is greater than 26
    # keep the segments that are in the dataframe
    cmd.remove(f'not resi {df[df["PDB Id"] == pdb]["Start"].values[0]}-{df[df["PDB Id"] == pdb]["End"].values[0]}')