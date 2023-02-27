import pandas as pd
import sys
import os

# functions
def getNegValueList(df, colName):
    negValueList = []
    for val in df[colName]:
        if val < 0:
            negValueList.append('true')
        else:
            negValueList.append('false')
    return negValueList

# Read in the csv file
df = pd.read_csv(sys.argv[1])

# Columns to keep
cols = ['Sequence','xShift','crossingAngle','axialRotation','zShift']

# Create a new dataframe with only the columns we want
df = df[cols]

# sort the dataframe by crossingAngle
df = df.sort_values(by='crossingAngle')

# create a new column for negCrossingAngle
# check if crossingAngle is negative
negCrossList = getNegValueList(df, 'crossingAngle')
negRotList = getNegValueList(df, 'axialRotation')

# append the list to the dataframe
df['negCrossingAngle'] = negCrossList
df['negAxialRot'] = negRotList

# make the crossingAngle column positive (can only pass positive values to the submit file)
df['crossingAngle'] = df['crossingAngle'].abs()
df['axialRotation'] = df['axialRotation'].abs()

# append the negCrossingAngle column to the dataframe after crossingAngle
cols = ['Sequence','xShift','crossingAngle','negCrossingAngle','axialRotation','negAxialRot','zShift']
df = df[cols]

# print the dataframe
print(df)

# Write the dataframe to a csv file
outputFile = os.path.splitext(sys.argv[1])[0] + '_redesign.csv'
df.to_csv(outputFile, index=False)