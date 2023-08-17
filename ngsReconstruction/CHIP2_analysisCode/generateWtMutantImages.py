'''
File: d:\github\Sequence-Design\ngsReconstruction\CHIP2_analysisCode\generateWtMutantImages.py
Project: d:\github\Sequence-Design\ngsReconstruction\CHIP2_analysisCode
Created Date: Wednesday August 16th 2023
Author: gjowl
-----
Last Modified: Wednesday August 16th 2023 8:11:18 pm
Modified By: gjowl
-----
Description: 
This script will accept an input file with a list of sequences, fluorescence, and ...
- bar graphs of wt sequence vs mutant aa percent
- 

-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------
'''

import sys, os, pandas as pd, numpy as np, matplotlib.pyplot as plt

# read in the input file
fluorFile = sys.argv[1]
outputDir = sys.argv[2]

os.makedirs(outputDir, exist_ok=True)

# read in the data 
fluorData = pd.read_csv(fluorFile, sep='\t', header=0) 

# TODO: 
# - get the mutant aa of each sequence 
# - extract just the dataframe for each WT sequence 
# - make a bar graph of the wt sequence vs the mutant aa percent 

