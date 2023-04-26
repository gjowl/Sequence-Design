#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   makeHelicalWheel.py
@Time    :   2023/04/25 15:49:25
@Author  :   Gilbert Loiseau 
@Version :   1.0
@Contact :   loiseau@wisc.edu
@License :   (C)Copyright 2023, Gilbert Loiseau
@Desc    :   None
'''

import os, sys, pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as pltcol
import matplotlib.patches as mpatches
from matplotlib.patches import Arc
import numpy as np
import math

# adapted from helixvis: https://github.com/subramv/helixvis/blob/master/helixvis/draw_wheel.py
def draw_wheel(sequence, output_dir, interface, colors = ["white", "red"], labels = False, labelcolor = "black", legend = False):
    min_num = 2
    max_num = 18
    num_colors = 4
    num_resid = len(sequence)
    ## 0 = hydrophobic, 1 = polar, 2 = basic, 3 = acidic
    #residues = {"A":0, "R":2, "N":1, "D":3, "C":1,
    #              "Q":1, "E":3, "G":0, "H":2, "I":0,
    #              "L":0, "K":2, "M":0, "F":0, "P":0,
    #              "S":1, "T":1, "W":0, "Y":0, "V":0}

    if num_resid not in range(min_num, max_num + 1):
        return "ERROR: sequence must have between 2 and 18 (inclusive) characters."
    #if len(colors) != 4:
    #    return "ERROR: parameter `colors` has missing or too many colors."
    for i in range(len(colors)):
        if colors[i] not in pltcol.cnames:
            return "ERROR: parameter `colors` has invalid colors." 

    # setting up the figure
    x_center = np.array([0, 0.8371, -0.2907, -0.7361, 0.5464, 0.5464, 
        -0.7361, -0.2907, 0.8371, 0, -0.8371, 0.2907, 0.7361, 
        -0.5464, -0.5464, 0.7361, 0.2907, -0.8371], dtype = 'f')
    y_center = np.array([0.85, -0.1476, -0.7987, 0.425, 0.6511, -0.6511, 
        -0.425, 0.7987, 0.1476, -0.85, 0.1476, 0.7987, -0.425, 
        -0.6511, 0.6511, 0.425, -0.7987, -0.1476], dtype = 'f')
    x_center = x_center/2 + 0.5
    y_center = y_center/2 + 0.5
    circle_radius = 0.0725
    circle_data = pd.DataFrame(data={'x': x_center[0:num_resid], 
        'y': y_center[0:num_resid], 'color': range(num_resid), 'type': range(num_resid)})

    # loop through the sequence and assign colors
    for i in range(num_resid):
        circle_data['color'][i] = colors[int(interface[i])]
        #circle_data['color'][i] = 'white'
        #circle_data['type'][i] = residues[sequence[i]]
        
    segment_data = pd.DataFrame(data={'xstart': x_center[0:num_resid - 1], 
        'ystart': y_center[0:num_resid - 1], 'xend': x_center[1:num_resid], 
        'yend': y_center[1:num_resid]})
    fig, ax = plt.subplots()
    for i in range(num_resid - 1):
        plt.plot([segment_data['xstart'][i], segment_data['xend'][i]], [segment_data['ystart'][i], segment_data['yend'][i]], 'ro-', color = 'black')
        
    for i in range(num_resid):
        circle = plt.Circle((circle_data['x'][i], circle_data['y'][i]), circle_radius, clip_on = False, zorder = 10, facecolor=circle_data['color'][i], edgecolor = 'black')
        ax.add_artist(circle)
        if labels:
            ax.annotate(sequence[i], xy=(circle_data['x'][i], circle_data['y'][i]), zorder = 15, fontsize=15, ha="center", va = "center", color = labelcolor)
        
        
    #if legend:
    #    restypes = set(circle_data['type'])
    #    handleid = []
    #    nonpolar = mpatches.Patch(color = colors[0], label = 'hydrophobic')
    #    polar = mpatches.Patch(color = colors[1], label = 'polar')
    #    basic = mpatches.Patch(color = colors[2], label = 'basic')
    #    acidic = mpatches.Patch(color = colors[3], label = 'acidic')
    #    if 0 in restypes:
    #        handleid = [nonpolar]
    #        
    #    if 1 in restypes:
    #        if bool(handleid):
    #            handleid.append(polar)
    #        else:
    #            handleid = [polar]
    #            
    #    if 2 in restypes:
    #        if bool(handleid):
    #            handleid.append(basic)
    #        else:
    #            handleid = [basic]
    #    
    #    if 3 in restypes:
    #        if bool(handleid):
    #            handleid.append(acidic)
    #        else:
    #            handleid = [acidic]
    #            
    #    plt.legend(handles = handleid, loc='center left', bbox_to_anchor=(1.04, 0.5))
        
    plt.axis('off')
    ax.set_aspect('equal')
    # save the figure
    fig.savefig(output_dir+'/'+sequence+'.png')
    # close the figure
    plt.close(fig)
    print("Saved figure for sequence: " + sequence)
    return fig, ax

if __name__ == '__main__':
    # read the command line arguments
    data_file = sys.argv[1]
    output_dir = sys.argv[2]

    # make the output directory if it doesn't exist
    os.makedirs(name=output_dir, exist_ok=True)

    # read in the data file
    data = pd.read_csv(data_file, dtype={'Sequence': str, 'Interface': str})

    # loop through the data file
    for sequence in data['Sequence']:
        # get the interface
        interface = data[data['Sequence'] == sequence]['Interface'].values[0]
        # create the helical wheel for the first 18 amino acids of the sequence
        print(draw_wheel(sequence[:-3], output_dir, interface, labels=True))
        exit(0)


