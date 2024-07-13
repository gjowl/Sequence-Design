import os, sys, pandas as pd, matplotlib.pyplot as plt, numpy as np, argparse

# initialize the parser
parser = argparse.ArgumentParser(description='Combines the sequence and energy files and plots the data')

# add the necessary arguments
parser.add_argument('-seqFile','--sequenceFile', type=str, help='the input WT design csv file')
parser.add_argument('-energyFile','--energyFile', type=str, help='the input energy csv file')
parser.add_argument('-outDir','--outputDir', type=str, help='the output directory')
parser.add_argument('-percentCutoff','--percentCutoff', type=float, help='the cutoff for the percent GpA')
parser.add_argument('-codeDir','--codeDir', type=str, help='the directory where the code is located')

# extract the arguments into variables
args = parser.parse_args()
sequenceFile = args.sequenceFile
energyFile = args.energyFile
outputDir = args.outputDir
percentGpA_cutoff = args.percentCutoff
codeDir = args.codeDir
os.makedirs(outputDir, exist_ok=True)

# read in the data files
sequence_df = pd.read_csv(sequenceFile)
energy_df = pd.read_csv(energyFile, dtype={'Interface': str})

# merge the dataframes by sequence
cols = ['Sequence', 'Total', 'VDWDimerOptimize', 'VDWMonomer', 'HBONDDimerOptimize', 'HBONDMonomer', 'IMM1DimerOptimize', 'IMM1Monomer', 'Design', 'PercentGpA', 'PercentStd', 'Type', 'Clash Mutant', 'Mutant Type', 'Position', 'Disruptive Mutant', 'PercentGpA_mutant', 'WT Sequence', 'Fluor Difference'] #TODO add more to carry over including the diffs; which for some reason are getting calcd again?
# check if all the columns are present, otherwise only keep the ones that are present
og_sequence_df = sequence_df.copy()
if all(col in sequence_df.columns for col in cols):
    sequence_df = sequence_df[cols]
else:
    # get the columns that are present
    cols = [col for col in cols if col in sequence_df.columns]
    sequence_df = sequence_df[cols]
sequence_df['Sequence'] = sequence_df['Sequence'].apply(lambda x: x[3:-3])
#energy_df['Sequence'] = energy_df['Directory'].apply(lambda x: x[3:-3])

# rename the DimerOptimize columns to Optimize
sequence_df.rename(columns={'VDWDimerOptimize': 'VDWOptimize', 'HBONDDimerOptimize': 'HBONDOptimize', 'IMM1DimerOptimize': 'IMM1Optimize'}, inplace=True)

# energy df columns to remove
energy_cols = ['Total', 'VDWOptimize', 'VDWMonomer', 'HBONDOptimize', 'HBONDMonomer', 'IMM1Optimize', 'IMM1Monomer']
energy_df = energy_df.drop(energy_cols, axis=1)

# keep the data for the sequenceAnalysis script
sequence_df.to_csv(f'{outputDir}/dataForSeqAnalysis.csv', index=False)

# keep only the sequences that are in the energy file
merged_df = sequence_df[sequence_df['Sequence'].isin(energy_df['Sequence'])]
df = merged_df.merge(energy_df, on='Sequence', how='left')
df.to_csv(f'{outputDir}/mergedEnergyData.csv', index=False)

# keep sequences not in the energy file
missing = sequence_df[~sequence_df['Sequence'].isin(energy_df['Sequence'])]
missing.to_csv(f'{outputDir}/missingSeqs.csv', index=False)
#df.rename(columns={'PercentGpA_transformed': 'PercentGpA', 'std_adjusted': 'PercentStd'}, inplace=True)

execPlot = f'python3 {codeDir}/analyzeData.py  -inFile {outputDir}/mergedEnergyData.csv -outDir {outputDir} -percentCutoff {percentGpA_cutoff}'
os.system(execPlot)