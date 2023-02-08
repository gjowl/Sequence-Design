import os, sys
import pandas as pd

# get the current working directory
cwd = os.getcwd()

# get the file with columns you want to get data for
colsFile = sys.argv[1]

# get the file with the data
dataFile = sys.argv[2]

# keep only the columns in data that are in cols
data = pd.read_csv(dataFile, header=0)
cols = pd.read_csv(colsFile, header=0)
data = data[cols.columns]
data.to_csv(cwd+'/' + dataFile + '_gblock.csv', index=False, header=False)