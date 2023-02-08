import os, sys
import pandas as pd


# get the current working directory
cwd = os.getcwd()

# get the file with sequences you want to get data for
seqsFile = sys.argv[1]

# get the file with the sequence data
seqDataFile = sys.argv[2]

# get the name of the file with the sequence data
seqDataFileName = seqDataFile.split('/')[-1]

# read in the files to pandas dataframes
seqs = pd.read_csv(seqsFile, header=0)
seqData = pd.read_csv(seqDataFile, header=0)

# keep only the rows in seqData that are in seqs
seqData = seqData[seqData['Sequence'].isin(seqs['Sequence'])]
seqData.to_csv(cwd+'/' + seqDataFileName + '_gblock.csv', index=False, header=False)
