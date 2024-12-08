import os, sys, pandas as pd
from pymol import cmd
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
'''
Run as: python3 createPymolSessionFiles.py {pdbOptimizedDir} {dataFile} {outputDir}
'''

def setupFrontviewPymol():
    # set background to white, oval length to 0.6, specular to 0
    cmd.bg_color('white'), cmd.set('cartoon_oval_length', 0.6), cmd.set('specular', 0)
    # show cartoon for chain B and spheres for chain A
    cmd.show('cartoon', 'chain A, chain B')
    # set the protein to color to white
    cmd.color('white')
    # turn y -90 and z 90 to orient the protein
    cmd.turn('y', -90), cmd.turn('z', 90)
    # set ray trace gain to 0, ray trace mode to 3, ray trace color to black, and depth cue to 0
    cmd.set('ray_trace_gain', 0), cmd.set('ray_trace_mode', 3), cmd.set('ray_trace_color', 'black'), cmd.set('depth_cue', 0)
    # set the ray shadow to 0 and opaque background to off
    cmd.set('ray_shadow', 0), cmd.set('ray_opaque_background', 0)
    # set the zoom for the figure to get the whole protein in the frame
    cmd.zoom('all', 2)

def setupSideviewPymol():
    # set background to white, oval length to 0.6, specular to 0
    cmd.bg_color('white'), cmd.set('cartoon_oval_length', 0.6), cmd.set('specular', 0)
    # show cartoon for chain B and spheres for chain A
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

def loadAlternatePdbs(df_sequence, pdbOptimizedDir):
    for i in range(len(df_sequence)):
        # get the directory name
        dirName, inner_dirName = df_sequence['Directory'][i], df_sequence['Geometry'][i]
        # get the design number by splitting the directory name by _
        designNum, repNum = inner_dirName.split('_')[1], df_sequence['replicateNumber'][i]
        # pdbName
        pdbName, sequence = str(repNum), df_sequence['Sequence'][i]
        # put together the filename
        filename = f'{pdbOptimizedDir}/{dirName}/{pdbName}.pdb'
        # load the pdb file with sequence as the name
        cmd.load(filename, sequence)
        print(f'Loaded {filename}')
        
def outputPseFiles(input_df, position_df, pdbOptimizedDir, output_dir):
    # loop through the dataframe
    cube_depth = 0
    for sequence, i in zip(input_df['Sequence'].unique(), range(len(input_df))):
        df_sequence = input_df[input_df['Sequence'] == sequence]
        df_sequence.reset_index(inplace=True)
        # get the one with the best energy
        df_sequence = df_sequence[df_sequence['Total'] == df_sequence['Total'].min()]
        print(df_sequence)
        setupSideviewPymol()
        # load through the alternate pdbs made by the pdbOptimization script
        try:
            loadAlternatePdbs(df_sequence, pdbOptimizedDir)
            print(f'Loaded optimized pdbs for {sequence}')
        except:
            print(f'No optimized pdbs for {sequence}')
        # this is fast, but kind of redundant: I should get a list of all of the interface pos and then loop through that
        for j in range(0, len(df_sequence['Interface'].unique()[0])):
            # get the names of the pdbs
            names = cmd.get_names()
            if df_sequence['Interface'].unique()[0][j] == '1':
                for name in names:
                    # select the current pdb
                    cmd.select('interface', name)
                    # color the residue for the current pdb
                    cmd.color('red', 'interface and resi '+str(j+23))
                    cmd.show('spheres', 'interface and resi '+str(j+23))
        # get the names of the current pdb
        current_pdb = f'{i}_{sequence}'
        cmd.set_name(sequence, current_pdb)
        # show spheres
        cmd.show('spheres')
        # check if i is divisible by 6
        if i % 6 == 0:
            # for every 4th pdb, move it deeper into the cube
            cube_depth += 30
        # get the ith position
        position = position_df.iloc[i]
        cmd.translate([position['x'], position['y'], cube_depth], current_pdb)
    cmd.save(f'{output_dir}/all.pse')

# read in the config argumenta
pdbOptimizedDir = sys.argv[1]
dataFile = sys.argv[2]
outputDir = sys.argv[3]

os.makedirs(name=outputDir, exist_ok=True)

# read into a dataframe
df = pd.read_csv(dataFile, sep=',', header=0, dtype={'Interface': str})

# get the datafile name
dataFilename = os.path.basename(dataFile).split('.')[0]

# check that the sequence starts with LLL and ends with ILI
if not df['Sequence'].str.startswith('LLL').all() or not df['Sequence'].str.endswith('ILI').all():
    # add LLL and ILI to the sequence
    df['Sequence'] = 'LLL' + df['Sequence'] + 'ILI' 

# get the total number of unique sequences
totalSeqs = len(df['Sequence'].unique())

# create an x and y coordinate for each sequence that corresponds to positions in a cube, add to the dataframe
position_df = pd.DataFrame()
# get the x and y coordinates for each sequence
position_df['x'] = [i for i in range(0, 6)]
# repeat this up to the total number of sequences
position_df['y'] = [i for i in range(0, 6)]
position_df = pd.concat([position_df]*int(totalSeqs/6))
# multiply to get the actual position in the cube
position_df['x'] = position_df['x']*20
position_df['y'] = position_df['y']*20
print(position_df)

# loop through the entire dataframe
df = df[df['PercentGpA'] > 0.4]
os.makedirs(name=outputDir, exist_ok=True)
#df.reset_index(inplace=True)
# save the dataframe
df.to_csv(f'{outputDir}/{dataFilename}_best.csv', index=False)
outputPseFiles(df, position_df, pdbOptimizedDir, outputDir)