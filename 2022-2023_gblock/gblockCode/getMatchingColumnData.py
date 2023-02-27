import os, sys
import pandas as pd

"""
 This file takes a file of design data and a file of columns to keep.
 It then extracts the directory column from the design data file and appends the replicateNumber column to it.
 This new column is then used to create a new column called Filename for the pdb files.
"""

# get the current working directory
cwd = os.getcwd()

# get the file with columns you want to get data for
colsFile = sys.argv[1]

# get the file with the data
dataFile = sys.argv[2]

# keep only the columns in data that are in cols
data = pd.read_csv(dataFile, header=0, dtype={'Interface': str})
cols = pd.read_csv(colsFile, header=0)
# extract the directory column from the data dataframe
dirCol = data["Directory"]
# split the directory column on the '_' character, save the second part of the split
dirCol = dirCol.str.split('_', expand=True)[1]
repNum = data["replicateNumber"]
# append the replicateNumber column to the directory column
dirCol = dirCol + '_' + repNum.astype(str) + '.pdb'

# append the directory column to the data
data["Filename"] = dirCol

# keep only the columns in data that are in cols
data = data[cols.columns]
# save the data to a csv file with the header
data.to_csv(cwd+'/' + dataFile + '_gblock.csv', index=False, header=True)