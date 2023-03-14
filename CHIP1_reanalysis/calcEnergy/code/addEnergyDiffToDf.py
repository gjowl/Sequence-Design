import os, sys, pandas as pd

# get the input data file from command line
dataFile = sys.argv[1]

# get the output directory from the data file
outputDir = os.getcwd()

# read in the data file
df = pd.read_csv(dataFile)

# define the energy terms
energyTerms = ['VDW', 'HBOND', 'IMM1']

# get the differences in energy between monomer and dimer
for term in energyTerms:
    df[f'{term}Diff'] = df[f'{term}DimerOptimize'] - df[f'{term}Monomer']

# save the data file
df.to_csv(f'{outputDir}/{dataFile}_energyDiff.csv', index=False)