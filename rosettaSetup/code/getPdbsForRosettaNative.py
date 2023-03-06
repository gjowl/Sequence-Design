import os, sys, pandas as pd

# get the command line arguments
sequenceFile = sys.argv[1]
dataFile = sys.argv[2]
pdbDir = sys.argv[3]
outputDir = sys.argv[4]

# check to see if the output directory exists
os.makedirs(name=outputDir, exist_ok=True)

# read in the input file as a pandas dataframe
df = pd.read_csv(sequenceFile)

# read in the data file as a pandas dataframe
df2 = pd.read_csv(dataFile)

# keep only the part of sequence outside of the first and last 3 residues
df['InterfaceSequence'] = df['Sequence'].str[3:-3]
df2['InterfaceSequence'] = df2['Sequence'].str[3:-3]

# only keep rows with matching sequence
df2 = df2[df2['InterfaceSequence'].isin(df['InterfaceSequence'])]

# get the pdb file names by splitting the directory by '_' and appending '_' and replicate number
df2['PDB'] = df2['Directory'].str.split('_').str[1] + '_' + df2['replicateNumber'].astype(str) + '.pdb'

# for each row in df2, get the toxgreenName from the sequenceFile
for index, row in df2.iterrows():
    sequence = row['InterfaceSequence']
    toxgreenName = df[df['InterfaceSequence'] == sequence]['toxgreenName'].values[0]
    df2.at[index, 'toxgreenName'] = toxgreenName

# output the file to a csv
df2.to_csv(f'{outputDir}/pdbs.csv', index=False)

# loop through the pdb files and copy them to the output directory with the correct name from sequenceFile
for index, row in df2.iterrows():
    pdb = row['PDB']
    pdbName = row['toxgreenName']
    os.system(f'cp {pdbDir}/{pdb} {outputDir}/{pdbName}.pdb')