import os, sys, pandas as pd, numpy as np

# energy difference function
def addEnergyDifferencesToDataframe(df, cols):
    for col in cols:
        df[f'{col}Diff'] = df[f'{col}DimerOptimize'] - df[f'{col}Monomer']
    return df

# read in the command line arguments
inputFile = sys.argv[1]
outputDir = sys.argv[2]
os.makedirs(outputDir, exist_ok=True)

# read in the input files as a dataframe
df = pd.read_csv(inputFile)

# add energy differences to the dataframe
cols = ['VDW', 'HBOND', 'IMM1']
df = addEnergyDifferencesToDataframe(df, cols)

# add the SASADiff column
#df['SasaDiff'] = df['SasaDimerOptimize'] - df['SasaMonomer']

# get the sequence column from the directory name
df['Sequence'] = df['Directory'].apply(lambda x: x[3:-3])

df.to_csv(f'{outputDir}/all_ala_energy_data_energyDifferences.csv', index=False)