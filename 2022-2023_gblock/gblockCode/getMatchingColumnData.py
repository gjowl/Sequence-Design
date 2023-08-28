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
mutantFile = sys.argv[3]

# keep only the columns in data that are in cols
data = pd.read_csv(dataFile, header=0, dtype={'Interface': str})
cols = pd.read_csv(colsFile, header=0)
mutants = pd.read_csv(mutantFile, header=0, dtype={'Interface': str})

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

# check if the value in the startAxialRotation column is negative
# if it is, set the value in the negRot column to True
# if it is not, set the value in the negRot column to False
data['negRot'] = data['startAxialRotation'].apply(lambda x: 'true' if x < 0 else 'false')
data['negAngle'] = data['startCrossingAngle'].apply(lambda x: 'true' if x < 0 else 'false')
# convert the startAxialRotation column to absolute values
data['startAxialRotation'] = data['startAxialRotation'].abs()
data['startCrossingAngle'] = data['startCrossingAngle'].abs()
# save the data to a csv file with the header
data.to_csv(cwd+'/' + dataFile + '_pdbBBRepackInput.csv', index=False, header=True)

output_df = pd.DataFrame()
for wt_seq in data['Sequence'].unique():
    mutant_df = mutants[mutants['Sequence'] == wt_seq].copy()
    wt_df = data[data['Sequence'] == wt_seq]
    # get the values for each column in the wt data
    for col in wt_df.columns:
        # if the column is not the sequence column
        if col != 'Sequence':
            # get the value for the column
            val = wt_df[col].iloc[0]
            # add the value to the mutant df
            mutant_df[col] = val
    # add the wt data to the mutant df by sequence
    mutant_df['Sequence'] = mutant_df['Mutant']
    mutant_df = mutant_df[wt_df.columns]
    output_df = pd.concat([output_df, mutant_df], ignore_index=True)
# if there are duplicates, append _1, _2, etc. to the end of the sequence
print(len(output_df))
output_df.drop_duplicates(subset=['Sequence'], inplace=True, keep='first')
output_df['Sequence'] = output_df['Sequence'].astype(str) + '_' + output_df.groupby('Sequence').cumcount().add(1).astype(str)
print(len(output_df))
output_df.to_csv(cwd+'/' + dataFile + '_pdbBBRepackInput_mutants.csv', index=False, header=True)