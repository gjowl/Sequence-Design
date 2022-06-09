import sys
import os
import pandas as pd

"""
run as:
    python3 compileBackboneOptimizedEnergyFiles.py [directory]

This file will compile all the energy files within all output directories
and output a single file with all the data.
"""

# get the directory from the command line
directory = sys.argv[1]

# setup the output dataframe
df = pd.DataFrame()

# get a list of all the directories in the directory
dirList = os.listdir(directory)

# trim the list of directories to only those that have LLL at the start
dirList = [x for x in dirList if x.startswith('LLL')]

colNames = ['Sequence', 'Total', 'Dimer', 'Monomer','DimerDiff','SASA','VDWDimer',
            'HBONDDimer','IMMIDimer','startXShift','xShift','xShiftDiff','startCrossingAngle',
            'crossingAngle','angleDiff','startAxialRotation','axialRotation','rotDiff',
            'startZShift','zShift','zShiftDiff']
# go through each directory and compile the energy files
for dir in dirList:
    # get the path to the directory
    dirPath = directory+dir
    # get a list of all the files in the directory
    fileList = os.listdir(dirPath)
    # get the energy file from the list of files
    energyFile = [file for file in fileList if file.endswith('energy.csv')][0]
    # get the path to the energy file
    energyFilePath = dirPath+'/'+energyFile
    try:
        # read in the energy file with no column names
        df_energy = pd.read_csv(energyFilePath, names=colNames)
        # concatenate the dataframe as a new row to the output dataframe
        df = pd.concat([df, df_energy], ignore_index=True)
    except:
        print('Error reading in energy file: '+energyFilePath)
        continue

# output the dataframe to a csv file
df.to_csv(directory+'/allEnergyFiles.csv')