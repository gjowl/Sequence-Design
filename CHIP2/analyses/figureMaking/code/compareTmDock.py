import os, sys, pandas as pd
from pymol import cmd
from PIL import Image

# read the command line arguments
tmDockDir = sys.argv[1]
pdbDir = sys.argv[2]
outputDir = sys.argv[3]

os.makedirs(name=outputDir, exist_ok=True)

# loop through the tmDock directory
for file in os.listdir(tmDockDir):
    # get the pdb name
    pdbName = file.split('.')[0]
    # get the pdb file
    # loop through the pdb directory
    for dir in os.listdir(pdbDir):
        # loop through each of the directories and search for the pdb file
        for pdb in os.listdir(f'{pdbDir}/{dir}'):
            # search for the pdb file
            if pdbName in pdb:
                # set the pdb file
                pdbFile = f'{pdbDir}/{dir}/{pdb}'
                # break out of the loop
                break
    # load the pdb file
    cmd.load(pdbFile)
    # load the tmDock file as tmdock
    cmd.load(f'{tmDockDir}/{file}', 'tmdock')
    # delete NEN and CEN in the tmdock
    cmd.remove('tmdock and name NEN, tmdock and name CEN')
    # check how many states the tmDock file has
    numStates = cmd.count_states('tmdock')
    # if numStates is greater than 1, then split the states
    if numStates > 1:
        cmd.split_states('tmdock')
    # delete the original tmdock
    cmd.delete('tmdock')
    # get the names of all structures in the tmdock
    names = cmd.get_names()
    # extract out any names that contain tmdock
    tmdock_names = [name for name in names if 'tmdock' in name]
    # loop through each of the names and get the Calpha RMSD
    rmsd_df = pd.DataFrame(columns=['Name', 'RMSD'])
    for name in tmdock_names:
        # align the name to the pdb
        cmd.align(name, pdbName)
        # get the Calpha RMSD
        rmsd = cmd.align(name, pdbName)[0]
        # add the name and rmsd to the dataframe
        rmsd_df = pd.concat([rmsd_df, pd.DataFrame([[name, rmsd]], columns=['Name', 'RMSD'])])
    if rmsd_df.shape[0] > 2:
        # sort the dataframe by the rmsd
        rmsd_df.sort_values(by=['RMSD'], inplace=True)
        # keep the highest and lowest rmsd
        rmsd_df = rmsd_df.iloc[[0, -1]]
        for name in tmdock_names:
            # if the name is not in the rmsd_df, then delete it
            if name not in rmsd_df['Name'].values:
                cmd.delete(name)
    # save the pymol session
    cmd.save(f'{outputDir}/{pdbName}.pse')
    # reset the pymol session
    cmd.reinitialize()


    