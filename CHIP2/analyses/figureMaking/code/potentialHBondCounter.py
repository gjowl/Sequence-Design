'''
File: /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/analyses/figureMaking/code/potentialHBondCounter.py
Project: /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/analyses/figureMaking/code
Created Date: Thursday February 8th 2024
Author: loiseau
-----
Description:
This script will count the number of potential hydrogen bonds in a protein. It will take in a pdb file,
find any oxygen atoms for desired amino acids on a backbone, and then output the number of potential hydrogen bonds
in the protein. 
-----
'''
import os, sys, pandas as pd, argparse
from pymol import cmd
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

# initialize the parser
parser = argparse.ArgumentParser(description='Appends the input datafile with the toxgreen data from another input datafile')

# add the necessary arguments
parser.add_argument('-pseDir','--pseDir', type=str, help='the raw data directory')
parser.add_argument('-outFile','--outputFile', type=str, help='the output csv file')
# add the optional arguments
parser.add_argument('-outDir','--outputDir', type=str, help='the output directory')

# extract the arguments into variables
args = parser.parse_args()
pseDir = args.pseDir
outputFile = args.outputFile
# default values for the optional arguments
outputDir = os.getcwd()
# if the optional arguments are not specified, use the default values
if args.outputDir is not None:
    outputDir = args.outputDir
    os.makedirs(outputDir, exist_ok=True)

def loadPdbAndGetBonds(filename, hbondAAs, ringAAs):
    # load the designed pdb file
    cmd.load(filename)
    # get the name of the pdb file without the extension
    sequence = filename.split('/')[-1].split('.')[0]
    # count the numbe of objects in the pdb file
    numObjs = len(cmd.get_names())
    # initialize the output dataframe
    output_df = pd.DataFrame(columns=['sequence', 'object_name', 'hbondAcceptors', 'hbondDonors'])
    # loop through the states of the pdb file
    for obj in cmd.get_names():
        # select this object
        cmd.select(obj)
        # loop through the chains of the object
        chainNames = []
        for chain in cmd.get_chains(obj):
            # select the chain
            chainName = f'{obj}_{chain}'
            chainNames.append(chainName)
            cmd.select(chainName, f'{obj} and chain {chain}')
            ## loop through the amino acids
            #for aa in hbondAAs:
            #    # select the chain atoms of the object
            #    #cmd.select(f'{obj}_tmp', f'{obj} and chain {chain} and resn "{aa}"')
            #    # get the number of atoms on the opposite chain that are within 1.5 angstroms of the oxygen atoms
            #    numHBonds = cmd.count_atoms(f'{obj} and name O and byres (chain {chain} and resn {ringAAs[0]}+{ringAAs[1]}+{ringAAs[2]}) within 1.5')
            #    print(numHBonds)
        donors, acceptors = 0, 0
        # get all of the chainName combinations
        combinations = [[chainNames[i], chainNames[j]] for i in range(len(chainNames)) for j in range(i+1, len(chainNames))]
        for combo in combinations:
            #numHbondA = cmd.count_atoms(f'{combo[0]} and name O and byres (resn {hbondAAs[0]}+{hbondAAs[1]}+{hbondAAs[2]}) within 3.3 of {combo[1]}')
            #numHbondB = cmd.count_atoms(f'{combo[1]} and name O and byres (resn {hbondAAs[0]}+{hbondAAs[1]}+{hbondAAs[2]}) within 3.3 of {combo[0]}')
            A_donors = cmd.count_atoms(f'{combo[0]} and name O within 3.3 of {combo[1]} and h.')
            A_acceptors = cmd.count_atoms(f'{combo[0]} and h. within 3.3 of {combo[1]} and name O')
            B_donors = cmd.count_atoms(f'{combo[1]} and name O within 3.3 of {combo[0]} and h.')
            B_acceptors = cmd.count_atoms(f'{combo[1]} and h. within 3.3 of {combo[0]} and name O')
        donors += A_donors + B_donors
        acceptors += A_acceptors + B_acceptors
        # add the data to the output dataframe using concat
        output_df = pd.concat([output_df, pd.DataFrame({'sequence': sequence, 'object_name': obj, 'hbondAcceptors': acceptors, 'hbondDonors': donors}, index=[0])])
    # close the pdb file
    cmd.reinitialize()
    return output_df

def measurePotentialHBonds(raw_data_dir, hbondAAs, ringAAs, output_dir, output_file):
    # initialize the output dataframe
    output_df = pd.DataFrame()
    # loop through the files in the rawDataDir
    for file in os.listdir(raw_data_dir):
        if file.endswith('.pse'):
            # get the filename
            filename = raw_data_dir+'/'+file
            # load the pdb file and get the hydrogen bonds
            bond_df = loadPdbAndGetBonds(filename, hbondAAs, ringAAs)
            output_df = pd.concat([output_df, bond_df])
    return output_df
    
            
if __name__ == '__main__':
    # define the hbondAAs and ringAAs (for now it doesn't seem like I'll need these? But I'll take a look again later)
    hbondAAs = ['SER', 'THR', 'GLY']
    ringAAs = ['PHE', 'TYR', 'TRP']
    
    # loop through the pseDir (which contains the directories of pse files for each design region)
    outputDf = pd.DataFrame()
    for d in os.listdir(pseDir):
        # define the current directory (current design region)
        currDir = f'{pseDir}/{d}'
        if os.path.isdir(currDir):
            # get the potential hydrogen bonds
            currHbonds = measurePotentialHBonds(currDir, hbondAAs, ringAAs, output_dir, outputFile)
            outputDf = pd.concat([outputDf, currHbonds])
    # save the output dataframe to a csv file
    outputDf.to_csv(f'{outputDir}/{outputFile}.csv', index=False)





# TODO:
# 1. Take functions from other scripts to read in pdb
# 2. Identify the given amino acids and their oxygen atoms from the pdb
# 3. Count the number of potential hydrogen bonds in the protein (using some distance cutoff for interhelical hydrogen bonds)
# 4. Output the number of potential hydrogen bonds in the protein
# 5. If time, could also try to change rotamers of the amino acids to see if the number of potential hydrogen bonds changes

