import os, sys, pandas as pd, argparse, numpy as np
from pymol import cmd

# initialize the parser
parser = argparse.ArgumentParser(description='Get the RMSD values for the CATM data against the optimized structures')

# add the necessary arguments
parser.add_argument('-dataFile','--dataFile', type=str, help='the data file with the CATM data and the optimized pdb data')
parser.add_argument('-catmDir','--catmDir', type=str, help='the directory with the raw data')
parser.add_argument('-pdbOptimizedDir','--pdbOptimizedDir', type=str, help='the directory with the optimized pdb files')
# add the optional arguments
parser.add_argument('-outputFile','--outputFile', type=str, help='the data file with the RMSD values')
parser.add_argument('-outputDir','--outputDir', type=str, help='the output directory')

# parse the arguments
args = parser.parse_args()
catmDir = args.catmDir
pdbOptimizedDir = args.pdbOptimizedDir
outputFile = 'rmsd_output' if args.outputFile is None else args.outputFile
outputDir = os.getcwd() if args.outputDir is None else args.outputDir
os.makedirs(name=outputDir, exist_ok=True)

def setupSideviewPymol():
    # set background to white, oval length to 0.6, specular to 0
    cmd.bg_color('white'), cmd.set('cartoon_oval_length', 0.6), cmd.set('specular', 0)
    # show cartoon
    cmd.show('cartoon', 'chain A, chain B')
    # set the protein to color to white
    cmd.color('white')
    # turn y -90 and z 90 to orient the protein
    cmd.turn('y', -90), cmd.turn('z', 90), cmd.turn('y', 90)
    # set ray trace gain to 0, ray trace mode to 3, ray trace color to black, and depth cue to 0
    cmd.set('ray_trace_gain', 0), cmd.set('ray_trace_mode', 3), cmd.set('ray_trace_color', 'black'), cmd.set('depth_cue', 0)
    # set the ray shadow to 0 and opaque background to off
    cmd.set('ray_shadow', 0), cmd.set('ray_opaque_background', 0)
    # set the zoom for the figure to get the whole protein in the frame
    cmd.zoom('all', 2)

if __name__ == '__main__':
    # open the data file
    dataFile = args.dataFile
    df = pd.read_csv(dataFile)

    # columns
    catm_cols = ['originalSeq', 'filename']
    repack_cols = ['Directory', 'replicateNumber']

    # define the output directories
    png_dir = f'{outputDir}/png/'
    pse_dir = f'{outputDir}/pse/'
    os.makedirs(name=png_dir, exist_ok=True)
    os.makedirs(name=pse_dir, exist_ok=True)

    # loop through the entire dataframe
    for index, row in df.iterrows():
        # get the catm sample
        inner_catm_dir = row[catm_cols[0]]
        catm_file = str(row[catm_cols[1]])
        catm = f'{catmDir}/{inner_catm_dir}/{catm_file}.pdb'
        # get the pdb file
        inner_pdb_dir = row[repack_cols[0]]
        pdb_file = str(row[repack_cols[1]])
        pdb = f'{pdbOptimizedDir}/{inner_pdb_dir}/{pdb_file}.pdb'
        # load the pdb and rename them
        cmd.load(catm)
        cmd.set_name(catm_file, 'CATM')
        cmd.load(pdb)
        cmd.set_name(pdb_file, 'Repack')
        # align the two structures
        cmd.align('Repack', 'CATM')
        # get the Calpha RMSD value
        rmsd = cmd.fit('Repack and name CA', 'CATM and name CA')
        setupSideviewPymol()
        # set catm color to green
        cmd.color('gray', 'CATM')
        # set repack color to blue
        cmd.color('orange', 'Repack')
        # save the image
        cmd.save(f'{png_dir}/{catm_file}_{pdb_file}.png')
        # save the session
        cmd.save(f'{pse_dir}/{catm_file}_{pdb_file}.pse')
        cmd.reinitialize()
        # add the rmsd value to the dataframe
        df.at[index, 'RMSD'] = rmsd
    # save the dataframe
    df.to_csv(f'{outputDir}/{outputFile}.csv', index=False)

    