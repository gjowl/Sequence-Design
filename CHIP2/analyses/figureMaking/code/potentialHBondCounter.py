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
    # count the numbe of objects in the pdb file
    numObjs = len(cmd.get_names())
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
        totalHbonds = 0
        totalHbonds_acc = 0
        # get all of the chainName combinations
        combinations = [[chainNames[i], chainNames[j]] for i in range(len(chainNames)) for j in range(i+1, len(chainNames))]
        for combo in combinations:
            print(combo)
            #numHbondA = cmd.count_atoms(f'{combo[0]} and name O and byres (resn {hbondAAs[0]}+{hbondAAs[1]}+{hbondAAs[2]}) within 3.3 of {combo[1]}')
            #numHbondB = cmd.count_atoms(f'{combo[1]} and name O and byres (resn {hbondAAs[0]}+{hbondAAs[1]}+{hbondAAs[2]}) within 3.3 of {combo[0]}')
            numHbondA = cmd.count_atoms(f'{combo[0]} and name O within 3.3 of {combo[1]} and h.')
            numHbondA_acc = cmd.count_atoms(f'{combo[0]} and h. within 3.3 of {combo[1]} and name O')
            numHbondB = cmd.count_atoms(f'{combo[1]} and name O within 3.3 of {combo[0]} and h.')
            numHbondB_acc = cmd.count_atoms(f'{combo[1]} and h. within 3.3 of {combo[0]} and name O')
        totalHbonds += numHbondA + numHbondB
        totalHbonds_acc += numHbondA_acc + numHbondB_acc
        print(totalHbonds, totalHbonds_acc)
        exit(0)
        #for chainNames:
        #    numHBonds = cmd.count_atoms(f'{obj} and name O and byres (chain {chain} and resn {hbondAAs[0]}+{hbondAAs[1]}+{hbondAAs[2]}) within 1.5')
        #    totalHbonds += numHBonds
        #print(totalHbonds)
    # close the pdb file
    cmd.reinitialize()

def measurePotentialHBonds(rawDataDir, hbondAAs, ringAAs, outputDir):
    # loop through the files in the rawDataDir
    for file in os.listdir(rawDataDir):
        if file.endswith('.pse'):
            # get the filename
            filename = rawDataDir+'/'+file
            print(filename)
            # load the pdb file and get the hydrogen bonds
            loadPdbAndGetBonds(filename, hbondAAs, ringAAs)
            
if __name__ == '__main__':
    # define the hbondAAs and ringAAs
    hbondAAs = ['SER', 'THR', 'GLY']
    ringAAs = ['PHE', 'TYR', 'TRP']
    #hbondAAs = ['S', 'T', 'G']
    #ringAAs = ['W', 'Y', 'F']
    # loop through the pseDir
    for dir in os.listdir(pseDir):
        currDir = pseDir+'/'+dir
        if os.path.isdir(currDir):
            # get the potential hydrogen bonds
            measurePotentialHBonds(currDir, hbondAAs, ringAAs, outputDir)





# TODO:
# 1. Take functions from other scripts to read in pdb
# 2. Identify the given amino acids and their oxygen atoms from the pdb
# 3. Count the number of potential hydrogen bonds in the protein (using some distance cutoff for interhelical hydrogen bonds)
# 4. Output the number of potential hydrogen bonds in the protein
# 5. If time, could also try to change rotamers of the amino acids to see if the number of potential hydrogen bonds changes

