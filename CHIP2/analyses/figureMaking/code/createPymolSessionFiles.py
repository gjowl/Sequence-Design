import os, sys, pandas as pd
from pymol import cmd

# read in the config arguments
rawDataDir = sys.argv[1]
dataFile = sys.argv[2]
outputDir = sys.argv[3]

os.makedirs(name=outputDir, exist_ok=True)

# read into a dataframe
df = pd.read_csv(dataFile, sep=',', header=0, dtype={'Interface': str})
# loop through the entire dataframe
for sample in df['Sample'].unique():
    df_sample = df[df['Sample'] == sample]
    os.makedirs(name=f'{outputDir}/{sample}', exist_ok=True)
    for sequence in df_sample['Sequence'].unique():
        df_sequence = df_sample[df_sample['Sequence'] == sequence]
        # get the directory name
        dirName = df_sequence['Directory'].unique()[0]
        # get the design number by splitting the directory name by _
        designNum, repNum = dirName.split('_')[1], df_sequence['replicateNumber'].unique()[0]
        # pdbName
        pdbName = designNum+'_'+str(repNum)
        # put together the filename
        filename = rawDataDir+'/'+pdbName+'.pdb'
        print(filename)
        # load the pdb file
        cmd.load(filename)
        # this is fast, but kind of redundant: I should get a list of all of the interface pos and then loop through that
        for j in range(0, len(df_sequence['Interface'].unique()[0])):
            # if the interface is 1
            if df_sequence['Interface'].unique()[0][j] == '1':
                # select the current pdb
                cmd.select('interface', pdbName)
                # color the residue for the current pdb
                cmd.color('red', 'interface and resi '+str(j+23))
        # show spheres
        cmd.show('spheres')
        # save the session file
        cmd.save(f'{outputDir}/{sample}/{sequence}.pse')
        # reset the pymol session
        cmd.reinitialize()