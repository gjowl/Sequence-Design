'''
File: /home/loiseau@ad.wisc.edu/github/Sequence-Design/ngsReconstruction/code/mutantAnalysis.py
Project: /home/loiseau@ad.wisc.edu/github/Sequence-Design/ngsReconstruction/code
Created Date: Friday August 4th 2023
Author: loiseau
-----
Last Modified: Friday August 4th 2023 1:39:38 pm
Modified By: loiseau
-----
Description:  
This file uses the following as inputs:
    - reconstructed fluorescence dataframe 
    - file with mutants and WT sequences and corresponding terms (currently energy and/or SASA)
It compares the fluorescence of the mutants to the WT sequence and outputs a dataframe with the 
percent difference of the mutant to the WT sequence. 
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------
'''

import sys, os, pandas as pd, numpy as np, matplotlib.pyplot as plt

# read in the reconstructed fluorescence dataframe
reconstructionFile = sys.argv[1]
sequenceMutantFile = sys.argv[2]

df_reconstruction = pd.read_csv(reconstructionFile, index_col=0)
df_sequenceMutant = pd.read_csv(sequenceMutantFile, index_col=0)