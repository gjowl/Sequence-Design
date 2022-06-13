import sys
import os
import pandas as pd
from functions import *

"""
Run as:
    python3 makeCalcPdbEnergyCsv.py [energyFile]

This converts a dataframe of energy files for my designed sequences into a 
csv file that can be used to run a local condor submit job on our server
to calculate the energy of pdbs.
"""

# read in energy file from command line 
energyFile = sys.argv[1]
df = pd.read_csv(energyFile)
# get just the mutants sequences
#df_designs = df[df['Sequence'] == df['StartSequence']]

# get the output directory (currently same directory as energy file)
programPath = os.path.realpath(energyFile)
programDir, programFile = os.path.split(programPath)
outputDir = programDir
outputDir = os.getcwd()

#the below makes a csv file for running condor backboneOptimizer on all of the mutant sequences
optimizeFile = outputDir+'/nonGxxxG_designs_calcEnergy.csv'
colsToAdd = ['Sequence','DesignDir']
with open(optimizeFile, 'w') as f:
    # loop through all rows to get the desired information for the csv for each sequence 
    for index, row in df.iterrows():
        # initialize string to output
        line = ''
        # loop through all of the given columns hardcoded above
        for col in colsToAdd:
            # kinda gross; needed to replace part of the dir path since I changed it recently, so coded it below to do so
            if 'Design' in col:
                #replace index 19-index for design with /Design_Data/12_06_2021_CHIP_dataset/
                value = str(row[col])
                start = value[:40]
                #TODO: edit this so that it get's the proper end if the design_number is longer/shorter
                # get the index of the parts of the path that won't be replaced
                designNumberIndex = value.find("/design")
                endDirPathIndex = value.find('backbone')
                pdbBeforeMutantDirIndex = value.find('/',endDirPathIndex)
                # for some reason, need to add 1 to include the / that I previously found
                pdbMiddle = value[designNumberIndex:pdbBeforeMutantDirIndex+1]
                pdbEnd = value[pdbBeforeMutantDirIndex:]
                replaceDir = '/Design_Data/12_06_2021_CHIP1_Dataset'
                newDir = start+replaceDir
                pdb = newDir+pdbMiddle+'mutants'+pdbEnd
                # uncomment this for WT
                #pdb = newDir+pdbMiddle+'bestOptimizedBackbone.pdb'
                line = line+','+pdb
            # needed to find a way to account for command line use of negative angle and rotation, coded that below
            else:
                value = str(row[col])
                if line == '':
                    line = value
                else:
                    line = line+','+value
        line = line + '\n'
        f.write(line)
f.close()

print('Generate csv file: ', optimizeFile)