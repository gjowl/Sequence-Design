import os, sys, pandas as pd

# read in the command line arguments
inputFile = sys.argv[1]
outputFile = sys.argv[2]
outputDir = sys.argv[3]

cwd = os.getcwd()

# read in the input file as a dataframe
df = pd.read_csv(inputFile)

# remove the first and last 6 residues
df['Sequence'] = df['Sequence'].apply(lambda x: x[3:-3])
#cols = ['Sequence', 'PercentGpA_transformed', 'std_adjusted','Total','VDWDiff','HBONDDiff','IMM1Diff','Sample','LB-12H_M9-36H']
cols = ['Sequence', 'PercentGpA_transformed', 'std_adjusted','Sample','LB-12H_M9-36H']
df = df[cols]
# rename the columns
df = df.rename(columns={'PercentGpA_transformed': 'PercentGpA', 'std_adjusted': 'PercentStd'})
# write the output file
df.to_csv(f'{outputDir}/{outputFile}.csv', index=False)