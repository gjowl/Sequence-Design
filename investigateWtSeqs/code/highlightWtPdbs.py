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

def getDesignPdb(df, sequence):
    # get the sequence in the alignment file that matches this one
    df_design = df[df['Sequence'] == sequence]
    # get the directory name
    dirName = df_design['Directory'].values[0]
    # get the design number by splitting the directory name by _
    designNum, repNum = dirName.split('_')[1], int(df_design['replicateNumber'].values[0])
    # pdbName
    pdbName = designNum+'_'+str(repNum)
    return dirName, pdbName

# read the command line arguments
wt_file = sys.argv[1]
align_file = sys.argv[2]
raw_data_dir = sys.argv[3]

# read the input file as a dataframe
df = pd.read_csv(wt_file, sep=',')
df_align = pd.read_csv(align_file, sep=',')

output_dir = 'output'
os.makedirs(output_dir, exist_ok=True)

# get all of the angles between -180 and -100
df_low = df[(df['Angle'] >= -180) & (df['Angle'] <= -100)]
df_high = df[(df['Angle'] >= 100) & (df['Angle'] <= 180)]

# convert angles less than or greater than 180 to their equivalent angles between 0 and 100 using loc
df_low['Angle'].apply(lambda x: 180 + x)
df_high['Angle'].apply(lambda x: x-180)

# replace the original values of the angles with the new values
df.update(df_low)
df.update(df_high)

# loop through the sequences
for pdb in df['PDB Id'].unique():
    # fetch the pdb file
    cmd.fetch(pdb)
    # get the pdb dataframe
    pdb_df = df[df['PDB Id'] == pdb]
    # keep the rows with unique segments
    pdb_df = pdb_df.drop_duplicates(subset=['Segment 1 #', 'Segment 2 #'])
    pdb_df = pdb_df.reset_index(drop=True)
    print(pdb_df)
    for index, row in pdb_df.iterrows():
        # get the chain letters
        chain1, chain2 = row['Chain 1'], row['Chain 2']
        # get the start and end positions
        start1, end1, start2, end2 = row['Seg 1 Pos start #'], row['Seg 1 Pos end #'], row['Seg 2 Pos start #'], row['Seg 2 Pos end #']
        # define the segments as selections
        segment = f'chain {chain1} and resi {start1}-{end1} or chain {chain2} and resi {start2}-{end2}'
        # select the segments
        cmd.select(f'segment_{index}', segment)
        # highlight the segments
        cmd.color('red', segment)
        # hide anything that is not the segments
        cmd.hide('everything', f'not segment_{index}')
        # get the axial distance and angle for this pdb
        axial_dist, axial_angle = row['Axial distance'], row['Angle']
        # get the Sequence_Match for this pdb
        seq_match = row['Sequence_Match']
        dirName, pdbName = getDesignPdb(df_align, seq_match)
        path = f'{raw_data_dir}/{dirName}/{pdbName}.pdb'
        # load in the pdb
        cmd.load(path)
        # align using super 
        cmd.super(f'segment_{index} and name CA', pdbName)
        rmsd = cmd.super(f'segment_{index} and name CA', pdbName)[0]
        #cmd.align(f'segment_{index} and name CA', pdbName)
        #rmsd = cmd.align(f'segment_{index} and name CA', pdbName)[0]
        rmsd = cmd.rms(f'segment_{index} and name CA', pdbName)
        print(f'RMSD: {rmsd}')
        # if the rmsd is less than 4, then save the pse
        # still looking for a good alignment method; some methods align poorly and give a low rmsd
        if rmsd < 4:
            cmd.save(f'{output_dir}/{pdb}_{index}.pse')
        # up to here, the code can align pdbs by structure and saves them if the rmsd is less than 4
        # TODO: highlight the residues that match the interface residues
        # get the interface residues
        #interface = df_align[df_align['Sequence'] == seqMatch]['Interface'].values[0]
        #print(interface)
        #exit(0)
        #for j in range(0, len(interface)):
        #    # if the interface is 1
        #    if interface[j] == '1':
        #        # select the current pdb
        #        cmd.select('interface', pdbName)
        #        # color the residue for the current pdb
        #        cmd.color('red', 'interface and resi '+str(j+23))
        # remove the pdb
        cmd.delete(pdbName)
        # remove the selection
        cmd.delete(f'segment_{index}')
        print(f'Finished {pdb}_{index}')
        print(f'Interface: {row["Interface1"], row["Interface2"]}')
        # recolor the segments
        cmd.color('green', segment)
    # reinitialize the pymol session
    cmd.reinitialize()