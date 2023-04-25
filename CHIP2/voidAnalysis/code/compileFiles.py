import sys
import pandas as pd
import os

"""
    Compiles energyFile.csv files from an input directory
"""

# get the current directory
cwd = os.getcwd()

# get the config file options
rawDataDir = sys.argv[1]
outputDir = sys.argv[2]
dataFile = sys.argv[3]
file_name = sys.argv[4]
delimiter = sys.argv[5]

# check if dataFile exists
if os.path.isfile(dataFile):
    # quit
    print('DataFile', dataFile,'exists. To overwrite, delete the file and run again.')
    sys.exit()

# define the output dataframe
outputDf = pd.DataFrame()

# get the parent directory
parentDir = os.path.dirname(rawDataDir)
# get the parent directory name
parentDirName = os.path.basename(parentDir)

# for each directory in the search directory
for dir in os.listdir(rawDataDir):
    # loop through the files in the directory
    # check if the directory is a directory
    currDir = f'{rawDataDir}/{dir}'
    if os.path.isdir(currDir):
        for file in os.listdir(currDir):
            # check filename
            if file == file_name:
                filename = f'{currDir}/{file}'
                # read the csv file into a dataframe
                header = pd.read_csv(filename,sep=delimiter,header=None, nrows=1)
                # read csv with interface column as string 
                df = pd.read_csv(filename, sep=delimiter, header=None, skiprows=1)# sets the interface column as a string
                df.columns = header.iloc[0]
                # add the directory name to the dataframe
                df['Directory'] = dir
                # combine the dataframes
                outputDf = pd.concat([outputDf,df],axis=0)

# rename the Sequence and Directory columns
outputDf = outputDf.dropna(axis=1, how='all')
outputDf = outputDf.rename(columns={'Sequence': 'Mutant', 'Directory': 'Sequence'})
# get rid of any empty columns
outputDf = outputDf.dropna(axis=1, how='all')
# output the dataframe to a csv file without the index
outputDf.to_csv(f'{outputDir}/{dataFile}', index=False)