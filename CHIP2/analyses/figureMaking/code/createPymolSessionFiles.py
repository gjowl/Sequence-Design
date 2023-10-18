import os, sys, pandas as pd
from pymol import cmd
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

def setupPymol():
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
        dirName, inner_dirName = df_sequence['Optimized_Directory'][i], df_sequence['Geometry'][i]
        # get the design number by splitting the directory name by _
        designNum, repNum = inner_dirName.split('_')[1], df_sequence['Optimized_replicateNumber'][i]
        # pdbName
        pdbName = str(repNum)
        # put together the filename
        filename = f'{pdbOptimizedDir}/{dirName}/{pdbName}.pdb'
        # load the pdb file
        cmd.load(filename)

def outputPseFiles(input_df, output_dir, pdbOptimizedDir):
    # loop through the dataframe
    for sample in input_df['Sample'].unique():
        df_sample = input_df[input_df['Sample'] == sample]
        pse_dir = f'{output_dir}/pse/{sample}'
        os.makedirs(name=pse_dir, exist_ok=True)
        df_sample.reset_index(inplace=True)
        for sequence in df_sample['Sequence'].unique():
            df_sequence = df_sample[df_sample['Sequence'] == sequence]
            df_sequence.reset_index(inplace=True)
            # get the directory name
            dirName = df_sequence['Directory'].unique()[0]
            # get the design number by splitting the directory name by _
            designNum, repNum = dirName.split('_')[1], df_sequence['replicateNumber'].unique()[0]
            # pdbName
            pdbName = designNum+'_'+str(repNum)
            # put together the filename
            filename = rawDataDir+'/'+pdbName+'.pdb'
            print(filename)
            # load the designed pdb file
            cmd.load(filename)
            # load through the alternate pdbs made by the pdbOptimization script
            loadAlternatePdbs(df_sequence, pdbOptimizedDir)
            # this is fast, but kind of redundant: I should get a list of all of the interface pos and then loop through that
            for j in range(0, len(df_sequence['Interface'].unique()[0])):
                # if the interface is 1
                if df_sequence['Interface'].unique()[0][j] == '1':
                    # select the current pdb
                    cmd.select('interface', pdbName)
                    # color the residue for the current pdb
                    cmd.color('red', 'interface and resi '+str(j+23))
            # show spheres
            cmd.show('spheres')
            # save the session file
            cmd.save(f'{pse_dir}/{sequence}.pse')
            # reset the pymol session
            cmd.reinitialize()

def outputPngs(input_df, output_dir):
# loop through the entire dataframe
    for sample in df['Sample'].unique():
        df_sample = df[df['Sample'] == sample]
        png_dir = f'{output_dir}/png/{sample}'
        os.makedirs(name=png_dir, exist_ok=True)
        df_sample.reset_index(inplace=True)
        for sequence in df_sample['Sequence'].unique():
            df_sequence = df_sample[df_sample['Sequence'] == sequence]
            df_sequence.reset_index(inplace=True)
            # get the directory name
            dirName = df_sequence['Directory'].unique()[0]
            # get the design number by splitting the directory name by _
            designNum, repNum = dirName.split('_')[1], df_sequence['replicateNumber'].unique()[0]
            # pdbName
            pdbName = designNum+'_'+str(repNum)
            # put together the filename
            filename = rawDataDir+'/'+pdbName+'.pdb'
            print(filename)
            # load the designed pdb file
            cmd.load(filename)
            # setup the pymol session for output
            setupPymol()
            for j in range(0, len(df_sequence['Interface'].unique()[0])):
                # if the interface is 1
                if df_sequence['Interface'].unique()[0][j] == '1':
                    # select the current pdb
                    cmd.select('interface', pdbName)
                    # color the residue for the current pdb
                    cmd.color('red', 'interface and resi '+str(j+23))
                    cmd.show('spheres', 'interface and resi '+str(j+23))
            # save the png file with a white background
            output_file = f'{png_dir}/{sequence}.png'
            cmd.png(output_file, width=1000, height=1000, ray=3, dpi=300)
            # reset the pymol session
            cmd.reinitialize()
            # get the total energy
            cols_to_output = ['Sequence', 'Interface', 'Total', 'PercentGpA', 'VDWDiff', 'HBONDDiff', 'IMM1Diff']
            # add text to image
            img = Image.open(output_file)
            draw = ImageDraw.Draw(img)
            # set the font size
            font_size = 30
            myfont = ImageFont.truetype("/mnt/c/Windows/fonts/Arial.ttf", font_size)
            for col, i in zip(cols_to_output,range(len(cols_to_output))):
                # get the value of interest from the dataframe and round to 2 decimal places
                value = df_sequence[col].unique()[0]
                # if the value is a float, round it to 2 decimal places
                if type(value) != str:
                    value = round(value, 2)
                draw.text((0, i*font_size), f'{col} = {value}', font=myfont, fill=(0,0,0))
            img.save(output_file)

# read in the config arguments
rawDataDir = sys.argv[1]
pdbOptimizedDir = sys.argv[2]
dataFile = sys.argv[3]
outputDir = sys.argv[4]

os.makedirs(name=outputDir, exist_ok=True)

# read into a dataframe
df = pd.read_csv(dataFile, sep=',', header=0, dtype={'Interface': str})

#outputPseFiles(df, outputDir, pdbOptimizedDir)
outputPngs(df, outputDir)