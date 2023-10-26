import os, sys, pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns
from boxplotFunctions import plotBoxplot

# read in the command line arguments
inputFile = sys.argv[1]
outputDir = sys.argv[2]

# read in the input files
df = pd.read_csv(inputFile, sep=',')
cols = ['PercentGpA_transformed', 'PercentGpA_Design']

for col in cols:
    if col == 'PercentGpA_Design':
        # keep only unique sequences
        df_sample = df.drop_duplicates(subset=['Sequence'])
        plotBoxplot(df_sample, col, outputDir)
    else:
        plotBoxplot(df, col, outputDir)
