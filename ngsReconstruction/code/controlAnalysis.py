'''
File: /home/loiseau@ad.wisc.edu/github/Sequence-Design/ngsReconstruction/code/controlAnalysis.py
Project: /home/loiseau@ad.wisc.edu/github/Sequence-Design/ngsReconstruction/code
Created Date: Friday August 4th 2023
Author: loiseau
-----
Last Modified: Friday August 4th 2023 1:39:48 pm
Modified By: loiseau
-----
Description: 
This file uses the following as inputs:
    - reconstructed fluorescence dataframe
It identifies the fluorescence of control sequences (marked in column segment as a non-numeric value),
creates a ... (curve?) of the fluorescence of the control sequences, and outputs a dataframe with the
...(something comparison to the for others sequences to controls). It is used specifically for my CHIP2
data for now to determine the designability of geometric regions for membrane proteins (maybe).
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------
'''

import sys, os, pandas as pd, numpy as np, matplotlib.pyplot as plt

# read in the reconstructed fluorescence dataframe
reconstructionFile = sys.argv[1]
df_reconstruction = pd.read_csv(reconstructionFile, index_col=0)

