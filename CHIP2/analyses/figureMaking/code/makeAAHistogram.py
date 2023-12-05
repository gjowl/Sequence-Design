import os, sys, pandas as pd, numpy as np
import matplotlib.pyplot as plt

# read in the command line arguments
sequenceFile = sys.argv[1]
outputDir = sys.argv[2]

# make the output directory if it doesn't exist
os.makedirs(name=outputDir, exist_ok=True)

# read in the sequence file
df = pd.read_csv(sequenceFile)

# keep only non-duplicated sequences
df = df.drop_duplicates(subset=['Sequence'])

# label the sequences as high or low based if percentGpA is above or below 0.5
df.loc[df['PercentGpA'] >= 0.5, 'Label'] = 'high'
df.loc[df['PercentGpA'] < 0.5, 'Label'] = 'low'

# define the aas to track
hbond_aas = ['T', 'S']
ring_aas = ['W', 'Y', 'F']

# create a histogram distribution of the number of hbond and ring aas at the interface
