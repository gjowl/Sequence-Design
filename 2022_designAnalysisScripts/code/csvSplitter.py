import sys
import pandas as pd
import os

"""
This code will take a list of csv files and combine them into a single csv file and wittle them down to a subset of the columns of the original files.
"""

# read in the directory location where the files are found
inputDir = sys.argv[1]
# get the current working directory
cwd = os.getcwd()
print(cwd)
inputDir = cwd + '/' + inputDir
# read in the list of columns to keep
columnsToKeep = sys.argv[2]
print(columnsToKeep)
# read in the columns to keep file
columnsToKeep = pd.read_csv(columnsToKeep, sep=',', header=None)
# get the header row
columnsToKeep = columnsToKeep.iloc[0]
# convert the columns to keep to a list
print(columnsToKeep)
# loop to navigate through the directories
outputDf = pd.DataFrame()
for dir in os.listdir(inputDir):
    # search for files ending with csv in the directory
    for file in os.listdir(inputDir+dir):
        # find file ending with csv and including top in filename
        if file.endswith('.csv') and 'top' in file:
            # read in the csv file
            df = pd.read_csv(inputDir+'/'+dir+'/'+file, sep=',', header=0, dtype={'Interface': str})
            # combine the directory name and the replicate number to get the pdb name
            designNumber = df.Directory.str.split('_').str[1]
            replicateNumber = df['replicateNumber']
            # convert the replicate number to a string list
            replicateNumber = replicateNumber.astype(str)
            # get the columns to keep
            df = df[columnsToKeep]
            # TODO: fix the dir name
            #df['pdb'] = pdbName
            df['dir'] = dir
            # append the dataframe to the output dataframe using concat
            outputDf = pd.concat([outputDf,df],axis=0)
        # sort output dataframe by total energy, VDWDiff, Region, and dir
        #outputDf = outputDf.sort_values(by=['Region', 'dir', 'Total', 'HBONDDiff'])
        #outputDf = outputDf.sort_values(by=['Total'])
        # output the file
        outputDf.to_csv(inputDir+'/combinedBestSequence.csv')