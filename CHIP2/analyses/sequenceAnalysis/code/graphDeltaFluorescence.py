import os, sys, pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns
from boxplotFunctions import plotBoxplot, plotMultiBoxplot

# read in the command line arguments
sequenceFile = sys.argv[1]
outputDir = sys.argv[2]

# read in the input files
df_seq = pd.read_csv(sequenceFile) 

# make the output directory
os.makedirs(outputDir, exist_ok=True)

yaxis = 'Delta Fluorescence'
xaxis = 'Sample'

# plot the boxplots
filename = os.path.basename(sequenceFile).split('.')[0]

df_seq.sort_values(by='Type', inplace=True)
for sample in df_seq['Sample'].unique():
    df_sample = df_seq[df_seq['Sample'] == sample]
    sample_outputDir = f'{outputDir}/{sample}'
    os.makedirs(sample_outputDir, exist_ok=True)
    df_sample.sort_values(by='Mutant Type')
    plotMultiBoxplot(df_sample, xaxis, yaxis, 'Mutant Type', sample_outputDir, ybottom=-1, ytop=1)