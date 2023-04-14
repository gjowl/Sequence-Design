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
        sasa_diff = seq_df[seq_df['Mutant'] == mutant]['SasaPercDifference'].values[0]
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