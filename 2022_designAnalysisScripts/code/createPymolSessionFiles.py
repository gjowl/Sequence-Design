from pymol import cmd
import os
import pandas as pd
import sys
from functions import *

# read in the config file
configFile = sys.argv[1]
globalConfig = read_config(configFile)
config = globalConfig['createPseScript']

# read in the config arguments
rawDataDir = config['rawDataDir']
outputDir = config['outputDir']
numSeqs = int(config['numSeqs'])

# find files in the output directory that contain the string top and end with csv
bestFiles = [f for f in os.listdir(outputDir) if 'top' in f and f.endswith('.csv')]

# loop through the best files
for file in bestFiles:
    # read into a dataframe
    print('Reading file', outputDir+'/'+file)
    df = pd.read_csv(outputDir+'/'+file, sep=',', header=0, dtype={'Interface': str})
    for i in range(0, numSeqs):
        # get the directory name
        dirName = df['Directory'][i]
        # get the design number by splitting the directory name by _
        designNum, repNum = dirName.split('_')[1], df['replicateNumber'][i]
        # get the replicate number
        repNum = df['replicateNumber'][i]
        # pdbName
        pdbName = designNum+'_'+str(repNum)
        # put together the filename
        filename = rawDataDir+'/'+dirName+'/'+pdbName+'.pdb'
        # load the pdb file
        cmd.load(filename)
        # loop through the interface
        # this is fast, but kind of redundant: I should get a list of all of the interface pos and then loop through that
        for j in range(0, len(df['Interface'][i])):
            # if the interface is 1
            if df['Interface'][i][j] == '1':
                # select the current pdb
                cmd.select('interface', pdbName)
                # color the residue for the current pdb
                cmd.color('red', 'interface and resi '+str(j+23))
    # show spheres
    cmd.show('spheres')
    # get region name from dataframe
    region = df['Region'][0]
    # save the session file
    cmd.save(outputDir+'/top'+str(numSeqs)+'_'+region+'.pse')
    # reset the pymol session
    cmd.reinitialize()