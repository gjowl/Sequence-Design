import os, sys, pandas as pd

# get the current working directory
cwd = os.getcwd()

# get the sequence file from the command line
seqFile = sys.argv[1]

# get the data file from the command line
dataFile = sys.argv[2]

# open the files as dataframes
seqDf = pd.read_csv(seqFile, header=0)
dataDf = pd.read_csv(dataFile, header=0)

# cut off the first 3 and last 3 characters of the sequence column
seqDf['Sequence'] = seqDf['Sequence'].str[3:-3]
dataDf['Sequence'] = dataDf['Sequence'].str[3:-3]

# keep only the data that has a sequence in the sequence file
dataDf = dataDf[dataDf['Sequence'].isin(seqDf['Sequence'])]

# output the dataframe to a csv file
dataDf.to_csv(f'{cwd}/seqData', sep=',', index=False)