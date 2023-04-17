from pymol import cmd
import os
import pandas as pd
import sys

# read in the config arguments
raw_data_dir = sys.argv[1]
input_file = sys.argv[2]
output_dir= sys.argv[3]

# make the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# read in the file as a dataframe
df = pd.read_csv(input_file, sep=',', header=0, dtype={'Interface': str})

# keep sequences that don't match the directory name
df = df[df['Sequence'] != df['Directory']]

# rename the sequence and directory columns
df = df.rename(columns={'Sequence': 'Mutant', 'Directory': 'Sequence'})

# get the Total energy by subtracting the Dimer from the Monomer
df['Total'] = df['Dimer'] - df['Monomer']

# find positions in sequence that are not the same in the mutant
df['Position'] = df.apply(lambda row: [i for i in range(len(row['Sequence'])) if row['Sequence'][i] != row['Mutant'][i]], axis=1)
# convert the position column to an integer
df['Position'] = df['Position'].apply(lambda x: int(x[0]))
# get the AA in the sequence for the position
df['WT_AA'] = df.apply(lambda row: row['Sequence'][row['Position']], axis=1)

# loop through each of the unique sequences
num_wrong = 0
for seq in df['Sequence'].unique():
    # get the sequence dataframe
    seq_df = df[df['Sequence'] == seq]
    # get the wildtype pdb path
    wildtype_pdb_path = f'{raw_data_dir}/{seq}/{seq}.pdb'
    try:
        cmd.load(wildtype_pdb_path, 'wildtype')
    except FileNotFoundError:
        num_wrong += 1
        print('Error loading: '+wildtype_pdb_path)
        print('Number wrong: '+str(num_wrong))
        continue
    except pymol.CmdException:
        num_wrong += 1
        print('Error loading: '+wildtype_pdb_path)
        print('Number wrong: '+str(num_wrong))
        continue
    # loop through the mutants
    for mutant in seq_df['Mutant'].unique():
        # get the mutant pdb path
        mutant_pdb_path = f'{raw_data_dir}/{seq}/{mutant}.pdb'
        # get the sasa difference
        sasa_diff = round(seq_df[seq_df['Mutant'] == mutant]['Total'].values[0], 2)
        # get the position
        position = seq_df[seq_df['Mutant'] == mutant]['Position'].values[0]+23
        # get the wildtype aa
        wt_aa = seq_df[seq_df['Mutant'] == mutant]['WT_AA'].values[0]
        # concat the position, wt_aa, and sasa_diff
        mutant_name = f'{position}_{wt_aa}_{sasa_diff}'
        # load the mutant pdb with the name as the position, wt aa, and % Sasa difference
        try:
            cmd.load(mutant_pdb_path, mutant_name)
        except FileNotFoundError('File not found: '+mutant_pdb_path):
            continue
        cmd.select('mutant', mutant_name)
        # color the residue for the current pdb
        cmd.color('red', 'mutant and resi '+str(position))
    # show spheres
    cmd.show('spheres')
    # save the session file
    cmd.save(f'{output_dir}/{seq}_mutants.pse')
    # reset the pymol session
    cmd.reinitialize()