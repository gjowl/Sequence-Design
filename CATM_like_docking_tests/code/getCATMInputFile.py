import os, sys, pandas as pd

# get the command line arguments
inputFile = sys.argv[1]
outputDir = sys.argv[2]

# get the input file name without the extension
inputFileName = os.path.splitext(os.path.basename(inputFile))[0]

# make the output directory if it doesn't exist
os.makedirs(outputDir, exist_ok=True)

# read in the data as a pandas dataframe
df = pd.read_csv(inputFile,header=0)

# get the sequence, directory, and replicate number columns
df = df[['Sequence', 'Directory', 'replicateNumber']]

# combine the directory and replicate number columns into a single column separated by an underscore
df['Directory'] = df['Directory'] + '_' + df['replicateNumber'].astype(str)

df = df[['Sequence', 'Directory']]
# remove rows with duplicate sequences, keeping the first occurrence
df = df.drop_duplicates(subset='Sequence', keep='first')
# sort the dataframe by the Directory column
df = df.sort_values(by=['Directory'])

# output the dataframe to a csv file
df.to_csv(f'{outputDir}/{inputFileName}_sequences.csv', index=False)