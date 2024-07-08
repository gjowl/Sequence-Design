import pandas as pd, os, sys, numpy as np, argparse
from pymol import cmd

# read in the command line arguments
parser = argparse.ArgumentParser(description='Create the interface for the datafile')
parser.add_argument('-datafile', help='The datafile to be analyzed')
parser.add_argument('-outputDir', help='The output directory for the interface files')

# parse through the arguments
args = parser.parse_args()
# necessary
if args.datafile:
    datafile = args.datafile
else:
    print('No datafile provided')
    sys.exit()
# optional
if args.outputDir:
    outputDir = args.outputDir
else:
    print('No output directory provided, using the current directory')
    outputDir = os.getcwd()

# Functions
# recreate the interface for the datafile

    # break down by length of each interface

    # add the correct number of 0s to the front of the sequence

    # combine into a new dataframe

if __name__ == '__main__':
    # read in the datafile (pdbOptimizationAnalysis/clash_dir/all/)
    data = pd.read_csv(datafile)

    # convert the interface column to a string
    data['Interface'] = data['Interface'].astype(str)

    # loop through the WT sequences
    for WTSequence in data['WTSequence'].unique():
        # keep all sequences of interest that match (WTSequence: the wt sequence)
        seqData = data[data['WTSequence'] == WTSequence]

        # keep the lowest energy for each sequence (Total: energy score)
        seqData = seqData[seqData['Total'] == seqData['Total'].min()]

        # start a pymol session
        cmd.reinitialize()
        # loop through the geometry for each (Geometry: column for seq_# corresponding to dir/#.pdb for each output run)
        for Geometry in seqData['Geometry']:
            # prepare the directory name

            # get the pdb filename

            # combine the names for the pdb to load 

            # read in the pdb from the directory
            cmd.load(f'{dirName}/dir_1.pdb')
            # rename the pdb (Type column?)

            # get the interface using the interface column

            # show the spheres

            # if WT, color the protein

            # if Mut, color the interface yellow
