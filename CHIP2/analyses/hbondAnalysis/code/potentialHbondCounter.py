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
parser.add_argument('-hbondDistance', '--hbondDistance', type=float, help='the distance cutoff for hydrogen bonds')

# extract the arguments into variables
args = parser.parse_args()
inputDir = args.pseDir
outputFile = args.outputFile
# default values for the optional arguments
outputDir = os.getcwd()
hbondDist = 3.3
# if the optional arguments are not specified, use the default values
if args.outputDir is not None:
    outputDir = args.outputDir
    os.makedirs(outputDir, exist_ok=True)
if args.hbondDistance is not None:
    hbondDist = args.hbondDistance

def loadPdbAndGetBonds(filename, hbondAAs, ringAAs, output_dir, hbondDist=3.3):
    # load the designed pdb file
    cmd.load(filename)
    # get the name of the pdb file without the extension
    sequence = filename.split('/')[-1].split('.')[0]
    # count the numbe of objects in the pdb file
    numObjs = len(cmd.get_names())
    # initialize the output dataframe
    output_df = pd.DataFrame()
    # loop through the states of the pdb file
    # create the output directory for the distance files
    distanceDir = f'{output_dir}/distances'
    os.makedirs(distanceDir, exist_ok=True)
    # open the hbond distance file
    f = open(f'{distanceDir}/{sequence}_hbondDistances.txt', 'w')
    for obj in cmd.get_names():
        # select this object
        cmd.select(obj)
        # loop through the chains of the object to get all of the chain combinations
        chainNames = []
        # initialize the donors and acceptors lists
        all_donors = []
        all_acceptors = []
        carbonyl_acceptors = []
        hbondDonors, hbondAcceptors = 0, 0
        for chain in cmd.get_chains(obj):
            # select the chain
            chainName = f'{obj}_{chain}'
            chainNames.append(chainName)
            cmd.select(chainName, f'{obj} and chain {chain}')
            # loop through the amino acids
            donors, acceptors = [], []
            donor_atoms, acceptor_atom = [], ''
            for aa in hbondAAs:
                # check if the amino acid is in the chain
                if not cmd.select(f'{obj} and chain {chain} and resn {aa}'):
                    continue
                # loop through the number of residues in the chain
                #TODO: fix this so it's not slow
                for res in range(1, cmd.count_atoms(f'{obj} and chain {chain} and name CA')):
                    # get the residue name 
                    # check the letter in the sequence
                    letter = sequence[res-1]
                    resName = ''
                    if letter == 'S':
                        resName = 'SER'
                    elif letter == 'T':
                        resName = 'THR'
                    elif letter == 'Y':
                        resName = 'TYR'
                    if resName == '':
                        continue
                    elif resName == 'SER':
                        donor_atoms.append('OG'), donor_atoms.append('HG1')
                        acceptor_atom = 'OG'
                    elif resName == 'THR':
                        donor_atoms.append('OG1'), donor_atoms.append('HG1')
                        acceptor_atom = 'OG1'
                    elif resName == 'TYR':
                        donor_atoms.append('OH'), donor_atoms.append('HH')
                        acceptor_atom = 'OH'
                # get the oxygen atoms for the amino acid
                for atom in donor_atoms:
                    donors.append(f'{obj} and chain {chain} and resi {res+22} and resn {aa} and name {atom}')
                acceptors.append(f'{obj} and chain {chain} and resi {res+22} and resn {aa} and name {acceptor_atom}')
                all_donors.append((chainName, donors))
                all_acceptors.append((chainName, acceptors))
            # get the carbonyl acceptors
            # loop through the number of residues in the chain
            for res in range(1, cmd.count_atoms(f'{obj} and chain {chain} and name CA')):
                # get the carbonyl oxygen
                #TODO: fix this hardcoding 22 which is the start number of the helix
                carbonyl_acceptors.append((chainName, f'{obj} and chain {chain} and resi {res+22} and name O'))
        # get all of the chainName combinations
        combinations = [[chainNames[i], chainNames[j]] for i in range(len(chainNames)) for j in range(i+1, len(chainNames))]
        # loop through the chain combinations and get the hydrogen bond donors and acceptors
        hbonds = 0
        # loop through all of the donors and acceptors
        hbondDonors = len(all_donors)
        hbondAcceptors = len(all_acceptors)
        # loop through the different combinations of donors and acceptors
        for donor_obj in all_donors:
            for acceptor_obj in all_acceptors:
                #make sure they are not the same object
                if donor_obj[0] == acceptor_obj[0]:
                    continue
                # get the donors and acceptors
                donors = donor_obj[1]
                acceptors = acceptor_obj[1]
                # get the number of hydrogen bonds between the donors and acceptors
                for donor in donors:
                    cmd.select('donor', f'{donor}')
                    for acceptor in acceptors:
                        cmd.select('acceptor', f'{acceptor}')
                        distance = cmd.distance('distance', 'donor', 'acceptor')
                        if distance < hbondDist:
                            hbonds += 1
                        f.write(f'{donor}, {acceptor}, {distance}\n')
        # loop through the carbonyl acceptors and get the number of hydrogen bonds
        for donor_obj in all_donors:
            for carbonyl_acceptor in carbonyl_acceptors:
                #make sure they are not the same object
                if donor_obj[0] == carbonyl_acceptor[0]:
                    continue
                # get the donors and acceptors
                donors = donor_obj[1]
                # get the number of hydrogen bonds between the donors and acceptors
                for donor in donors:
                    cmd.select('donor', f'{donor}')
                    cmd.select('acceptor', f'{carbonyl_acceptor[1]}')
                    distance = cmd.distance('distance', 'donor', 'acceptor')
                    if distance < hbondDist:
                        hbonds += 1
                    f.write(f'{donor}, {carbonyl_acceptor[1]}, {distance}\n')
        for combo in combinations:
            #cmd.select(f'{combo[1]}_donors', f'donors_{combo[1]} within {hbondDist} of acceptors_{combo[0]}')
            # initialize the number of donors and acceptors
            calpha_donors, calpha_acceptors = 0, 0
            # define the donors and acceptors for each chain
            A_calpha_donors = f'{combo[0]} and name O within 2.69 of {combo[1]} and name HA'
            A_calpha_acceptors = f'{combo[0]} and name HA within 2.69 of {combo[1]} and name O'
            B_calpha_donors = f'{combo[1]} and name O within 2.69 of {combo[0]} and name HA'
            B_calpha_acceptors = f'{combo[1]} and name HA within 2.69 of {combo[0]} and name O'
            # select the donors and acceptors and name them by the chain combination
            cmd.select(f'calpha_donors_{combo[0]}', f'{A_calpha_donors}')
            cmd.select(f'calpha_donors_{combo[1]}', f'{B_calpha_donors}')
            cmd.select(f'calpha_acceptors_{combo[0]}', f'{A_calpha_acceptors}')
            cmd.select(f'calpha_acceptors_{combo[1]}', f'{B_calpha_acceptors}')
            # add them to the total count
            calpha_donors = calpha_donors + cmd.count_atoms(f'calpha_donors_{combo[0]}') + cmd.count_atoms(f'calpha_donors_{combo[1]}')
            calpha_acceptors = calpha_acceptors + cmd.count_atoms(f'calpha_acceptors_{combo[0]}') + cmd.count_atoms(f'calpha_acceptors_{combo[1]}')
            output_df = pd.concat([output_df, pd.DataFrame({'Sequence': sequence, 'object_name': obj, 'hbonds': hbonds, 'hbondDonors': hbondDonors, 'hbondAcceptors': hbondAcceptors, 'c-alphaDonors':calpha_donors, 'c-alphaAcceptors':calpha_acceptors}, index=[0])])
            #print(output_df)
        # add the data to the output dataframe using concat
    # close the hbond distance file
    f.close()
    # save the session file
    cmd.save(f'{output_dir}/{sequence}.pse')
    # close the pdb file
    cmd.reinitialize()
    return output_df

def measurePotentialHBonds(raw_data_dir, hbondAAs, ringAAs, output_dir, hbondDist):
    # initialize the output datafram
    output_df = pd.DataFrame()
    # loop through the files in the rawDataDir
    for file in os.listdir(raw_data_dir):
        if file.endswith('.pse'):
            # get the filename
            filename = raw_data_dir+'/'+file
            # load the pdb file and get the hydrogen bonds
            bond_df = loadPdbAndGetBonds(filename, hbondAAs, ringAAs, output_dir, hbondDist)
            output_df = pd.concat([output_df, bond_df])
    return output_df
    
            
if __name__ == '__main__':
    # define the hbondAAs and ringAAs (for now it doesn't seem like I'll need these? But I'll take a look again later)
    hbondAAs = ['SER', 'THR', 'TYR']
    ringAAs = ['PHE', 'TYR', 'TRP']
    
    # loop through the pseDir (which contains the directories of pse files for each design region)
    outputDf = pd.DataFrame()
    for d in os.listdir(inputDir):
        # define the current directory (current design region)
        currDir = f'{inputDir}/{d}'
        if os.path.isdir(currDir):
            print(currDir)
            # make the output directory for the pse files
            pseDir = f'{outputDir}/pse/{d}'
            os.makedirs(pseDir, exist_ok=True)
            # get the potential hydrogen bonds
            currHbonds = measurePotentialHBonds(currDir, hbondAAs, ringAAs, pseDir, hbondDist)
            outputDf = pd.concat([outputDf, currHbonds])
    # save the output dataframe to a csv file
    outputDf.to_csv(f'{outputDir}/{outputFile}.csv', index=False)





# TODO:
# 1. Take functions from other scripts to read in pdb
# 2. Identify the given amino acids and their oxygen atoms from the pdb
# 3. Count the number of potential hydrogen bonds in the protein (using some distance cutoff for interhelical hydrogen bonds)
# 4. Output the number of potential hydrogen bonds in the protein
# 5. If time, could also try to change rotamers of the amino acids to see if the number of potential hydrogen bonds changes

