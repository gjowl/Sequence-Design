import os, sys, pandas as pd

# read the command line arguments
interfaceFile = sys.argv[1]
dataFile = sys.argv[2]
mutantFile = sys.argv[3]
outputFile = sys.argv[4]

# read the input file and the file to merge as dataframes
df = pd.read_csv(dataFile, sep=',', dtype={'Interface': str})
interfaceDf = pd.read_csv(interfaceFile, sep=',', dtype={'Interface': str, 'replicateNumber': str})
mutantDf = pd.read_csv(mutantFile, sep=',', dtype={'Interface': str, 'replicateNumber': str})

# merge all columns of the mutantDf with the data df
df = pd.merge(mutantDf, df, on='Sequence', how='left')

# replace the interface column with the interfaceDf interface column
df['Interface'] = interfaceDf['Interface']

# output the dataframe to a csv file without the index
df.to_csv(f'{outputFile}.csv', index=False)