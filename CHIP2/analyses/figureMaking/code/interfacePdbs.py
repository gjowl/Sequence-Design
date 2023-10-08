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

if __name__ == '__main__':
    # read the command line arguments
    raw_data_dir = sys.argv[1]
    data_file = sys.argv[2]
    output_dir = sys.argv[3]

    # make the output directory if it doesn't exist
    os.makedirs(name=output_dir, exist_ok=True)
    png_dir, pse_dir = output_dir+'/png', output_dir+'/pse'

    # make the png and pse directories if they don't exist
    os.makedirs(name=output_dir+'/png', exist_ok=True)
    os.makedirs(name=output_dir+'/pse', exist_ok=True)

    # read in the data file
    df = pd.read_csv(data_file, sep=',', dtype={'Interface': str})

    # loop through the entire dataframe
    for i in range(len(df)):
        # get the directory name
        dirName = df['Directory'][i]
        sample = df['sample'][i]
        # get the design number by splitting the directory name by _
        designNum, repNum = dirName.split('_')[1], df['replicateNumber'][i]
        # pdbName
        pdbName = designNum+'_'+str(repNum)
        # put together the filename
        filename = raw_data_dir+'/'+dirName+'/'+pdbName+'.pdb'
        # load the pdb file
        cmd.load(filename)
        # setup the pymol session for output
        setupPymol()
        # get the interface positions as a residue string
        selection_string = getInterfacePos(df['Interface'][i])
        cmd.select('interface', selection_string)
        # color the residue for the current pdb on chain A
        cmd.color('red', 'interface and chain A')
        # save the session file and png file
        cmd.save(pse_dir+'/'+pdbName+'.pse')
        cmd.png(png_dir+'/'+pdbName+'.png', width=1000, height=1000, ray=3, dpi=300)
        # reset the pymol session
        cmd.reinitialize()