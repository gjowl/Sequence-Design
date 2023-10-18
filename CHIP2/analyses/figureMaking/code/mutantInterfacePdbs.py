#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   makeInterfacePdbs.py
@Time    :   2023/04/25 13:59:44
@Author  :   Gilbert Loiseau 
@Version :   1.0
@Contact :   loiseau@wisc.edu
@License :   (C)Copyright 2023, Gilbert Loiseau
@Desc    :   Makes a structure file with the interface highlighted for each design in the input data_file.
             Outputs a pymol session file and a png file for each design into respective png and pse directories.

@Usage   :   python3 interfacePdbs.py raw_data_directory data_file output_directory
'''

import os, sys, pandas as pd
import pymol.cmd as cmd

def setupPymol():
    # set background to white, oval length to 0.6, specular to 0
    cmd.bg_color('white'), cmd.set('cartoon_oval_length', 0.6), cmd.set('specular', 0)
    # show cartoon for chain B and spheres for chain A
    cmd.show('cartoon', 'chain B'), cmd.show('spheres', 'chain A')
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

def getInterfaceString(input_df, i, output_dir, aas=''):
    selection_string = getInterfacePos(input_df['Interface'][i])
    if aas != '':
        selection_string = getAAPositions(input_df['Directory'][i], aas)
    return selection_string

def getInterfacePos(interface):
    interface_pos = []
    for j in range(0, len(interface)):
        # if the interface is 1
        if interface[j] == '1':
            # add the interface to a list
            interface_pos.append(j+23)
    # create the selection string
    interface_string = 'resi '
    for j in interface_pos:
        interface_string += str(j)+','
    return interface_string 

def getAAPositions(sequence, aas):
    pos = []
    for j in range(0, len(sequence)):
        # check if the amino acid is in the list
        if sequence[j] in aas:
            # add the interface to a list
            pos.append(j+23)
    # create the selection string
    pos_string = 'resi '
    for j in pos:
        pos_string += str(j)+','
    return pos_string 

def saveInterfacePngs(input_df, i, output_dir, aas=''):
    # get the interface positions as a residue string
    selection_string = getInterfaceString(input_df, i, output_dir, aas)
    if selection_string == 'resi ':
        return
    cmd.select('interface', selection_string)
    # color the residue for the current pdb on chain A
    cmd.color('red', 'interface and chain A')
    # save the session file and png file
    os.makedirs(name=output_dir, exist_ok=True)
    #cmd.save(f'{pse_dir}/{inner_dirName}.pse')
    cmd.png(f'{output_dir}/{inner_dirName}.png', width=1000, height=1000, ray=3, dpi=300)
    cmd.color('white', 'interface and chain A')

def saveInterfacePse(input_df, output_file, output_dir, aas='', bothChains=False):
    # get the interface positions as a residue string
    selection_string = getInterfaceString(input_df, i, output_dir, aas)
    cmd.select('interface', selection_string)
    # color the residue for the current pdb
    if bothChains:
        cmd.color('red', 'interface')
        cmd.hide('spheres', 'chain A')
        cmd.show('spheres', 'interface')
    else:
        cmd.color('red', 'interface and chain A')
    # save the session file and png file
    os.makedirs(name=output_dir, exist_ok=True)
    cmd.save(f'{output_dir}/{output_file}.pse')

def saveInterfacePseBothChains(input_df, output_file, output_dir):
    # get the interface positions as a residue string
    selection_string = getAAPositions(input_df['Directory'][0], aas)
    cmd.select('interface', selection_string)
    # color the residue for the current pdb on chain A
    cmd.color('red', 'interface and chain A')
    # save the session file and png file
    os.makedirs(name=output_dir, exist_ok=True)
    cmd.save(f'{output_dir}/{output_file}.pse')

def outputPngs(input_df, output_dir, hbondAAs, ringAAs):
# loop through the entire dataframe
    for sample in df['Sample'].unique():
        df_sample = df[df['Sample'] == sample]
        png_dir = f'{output_dir}/png/{sample}'
        os.makedirs(name=png_dir, exist_ok=True)
        df_sample.reset_index(inplace=True)
        # loop through the dataframe
        for i in range(len(df_sample)):
            # get the directory name
            dirName, inner_dirName = df_sample['Directory'][i], df_sample['Geometry'][i]
            # get the design number by splitting the directory name by _
            designNum, repNum = inner_dirName.split('_')[1], df_sample['replicateNumber'][i]
            # pdbName of the optimized pdb
            pdbName = str(repNum)
            # put together the filename
            filename = f'{raw_data_dir}/{dirName}/{pdbName}.pdb'
            # load the pdb file
            cmd.load(filename)
            # setup the pymol session for output
            setupPymol()
            interfaceDir, hbondDir, ringDir = f'{png_dir}/interface', f'{png_dir}/hbond', f'{png_dir}/ring'
            saveInterfacePngs(df_sample, i, interfaceDir)
            saveInterfacePngs(df_sample, i, hbondDir, hbondAAs)
            saveInterfacePngs(df_sample, i, ringDir, ringAAs)
            # reset the pymol session
            cmd.reinitialize()

def outputPses(input_df, output_dir):
    for sample in input_df['Sample'].unique():
        df_sample = input_df[input_df['Sample'] == sample]
        for sequence in df_sample['Directory'].unique():
            df_sequence = df_sample[df_sample['Directory'] == sequence]
            pse_dir = f'{output_dir}/pse/{sample}'
            os.makedirs(name=pse_dir, exist_ok=True)
            df_sequence.reset_index(inplace=True)
            # loop through the dataframe
            for i in range(len(df_sequence)):
                # get the directory name
                dirName, inner_dirName = df_sequence['Directory'][i], df_sequence['Geometry'][i]
                # get the design number by splitting the directory name by _
                designNum, repNum = inner_dirName.split('_')[1], df_sequence['replicateNumber'][i]
                # pdbName
                pdbName = str(repNum)
                # put together the filename
                filename = f'{raw_data_dir}/{dirName}/{pdbName}.pdb'
                # load the pdb file
                cmd.load(filename)
            setupPymol()
            saveInterfacePse(df_sequence, sequence, pse_dir, bothChains=True)
            # reset the pymol session
            cmd.reinitialize()

if __name__ == '__main__':
    # read the command line arguments
    raw_data_dir = sys.argv[1]
    data_file = sys.argv[2]
    output_dir = sys.argv[3]

    # make the output directory if it doesn't exist
    os.makedirs(name=output_dir, exist_ok=True)

    # read in the data file
    df = pd.read_csv(data_file, sep=',', dtype={'Interface': str})

    df = df[df['PercentGpA'] > 0.5]

    # setup lists of aas to evaluate
    hbondAAs = ['S', 'T', 'G']
    ringAAs = ['W', 'Y', 'F']
    AAs = ['S', 'T', 'G', 'W', 'Y', 'F']

    outputPngs(df, output_dir, hbondAAs, ringAAs)
    outputPses(df, output_dir)