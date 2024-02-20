import os, sys, pandas as pd, argparse
from pymol import cmd

# initialize parser
parser = argparse.ArgumentParser(description='Read through a list of hbond files for a specific protein and create a pymol session file with all the potential hbonds visualized.')

# add arguments
parser.add_argument('-inFile','--inputFile', type=str, help='File with the names of the proteins to find.')
parser.add_argument('-hbondsDir','--hbondsDir', type=str, help='List of hbond files to read through.')
parser.add_argument('-pseDir','--pseDir', type=str, help='Directory containing the pymol session files.')
# add the optional argument
parser.add_argument('-outputDir','--output_dir', type=str, help='Directory to save the pymol session files to.')
parser.add_argument('-hbondDistance','--hbondDistance', type=float, help='The distance cutoff for a hydrogen bond.')

# read arguments from the command line
args = parser.parse_args()
inFile = args.inputFile
hbondsDir = args.hbondsDir
pseDir = args.pseDir
outputDir = os.getcwd() if args.output_dir is None else args.output_dir
hbondDistance = args.hbondDistance
os.makedirs(outputDir, exist_ok=True)

def setupPymol():
    # set the color to their defaults
    for object in cmd.get_object_list():
        cmd.color('red', f'{object} and e. O')
        cmd.color('blue', f'{object} and e. N')
        cmd.color('green', f'{object} and e. C')
        cmd.color('white', f'{object} and e. H')
    # set the background to black
    cmd.bg_color('black')
    # hide everything and show cartoon
    cmd.hide('everything')
    cmd.show('cartoon')

if __name__ == '__main__':
    # read the input file
    input_df = pd.read_csv(inFile)
    
    # read through the list of hbond files
    for sequence in input_df['Sequence']:
        # look for the protein name in the hbonds directory
        if not os.path.exists(f'{hbondsDir}/{sequence}.txt'):
            print(f'No hbond file found for {sequence}.')
            continue
        # read the hbond file as a dataframe, skipping the first row
        df = pd.read_csv(f'{hbondsDir}/{sequence}.txt', sep=',', skiprows=1)
        # only keep the rows with a distance less than the cutoff
        df = df[df['distance'] < hbondDistance]
        # reset the index
        df.reset_index(drop=True, inplace=True)
        print(sequence)
        # get the sample name
        sample = input_df[input_df['Sequence'] == sequence]['Sample'].values[0]
        # create a pymol session file
        cmd.load(f'{pseDir}/{sample}/{sequence}.pse')
        setupPymol()
        for index, row in df.iterrows():
            # keep the string up to the 4th 'and' in the row['donor']
            donor = row['donor'].split(' and')
            obj = donor[0]
            donor = ' and'.join(donor[:4])
            acceptor = row['acceptor'].split(' and')
            acceptor = ' and'.join(acceptor[:4])
            cmd.select(f'{obj}_hbond_pair_{index}', f'{donor} + {acceptor}')
            cmd.show('spheres', f'{obj}_hbond_pair_{index}')
            print(donor, acceptor)
        # save the pymol session file
        cmd.save(f'{outputDir}/{sequence}.pse')
        cmd.reinitialize()
