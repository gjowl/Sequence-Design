import os, sys, pandas as pd, matplotlib.pyplot as plt, numpy as np, argparse

# initialize the parser
parser = argparse.ArgumentParser(description='Combines the sequence and energy files and plots the data')

# add the necessary arguments
parser.add_argument('-seqFile','--sequenceFile', type=str, help='the input WT design csv file')
parser.add_argument('-energyFile','--energyFile', type=str, help='the input energy csv file')
parser.add_argument('-outDir','--outputDir', type=str, help='the output directory')

# extract the arguments into variables
args = parser.parse_args()
sequenceFile = args.sequenceFile
energyFile = args.energyFile
outputDir = args.outputDir
os.makedirs(outputDir, exist_ok=True)

# read in the data files
sequence_df = pd.read_csv(sequenceFile)
energy_df = pd.read_csv(energyFile)

# merge the dataframes by sequence
cols = ['Sequence', 'PercentGpA', 'PercentStd', 'Type', 'Clash Mutant', 'Mutant Type', 'Position', 'Disruptive Mutant', 'PercentGpA_mutant', 'WT Sequence', 'Fluor Difference', 'PercentGpA_transformed', 'std_adjusted,'] #TODO add more to carry over including the diffs; which for some reason are getting calcd again?
# check if all the columns are present, otherwise only keep the ones that are present
if all(col in sequence_df.columns for col in cols):
    sequence_df = sequence_df[cols]
else:
    # get the columns that are present
    cols = [col for col in cols if col in sequence_df.columns]
    sequence_df = sequence_df[cols]
sequence_df['Sequence'] = sequence_df['Sequence'].apply(lambda x: x[3:-3])
energy_df['Sequence'] = energy_df['Directory'].apply(lambda x: x[3:-3])

# keep only the sequences that are in the energy file
sequence_df = sequence_df[sequence_df['Sequence'].isin(energy_df['Sequence'])]
df = sequence_df.merge(energy_df, on='Sequence', how='left')

# get the sequence filename
seqFilename = sequenceFile.split('/')[-1].split('.')[0]
df.to_csv(f'{outputDir}/{seqFilename}_merged.csv', index=False)