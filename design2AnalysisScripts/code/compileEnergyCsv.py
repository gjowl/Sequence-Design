import sys
import pandas as pd
import os

"""
    Compiles energyFile.csv files from an input directory
"""

# get the path to the current directory
currentDir = os.getcwd()

# get the current working directory
cwd = os.getcwd()+"/"

# define the search directory
searchDir = cwd+sys.argv[1]

# define the output dataframe
outputDf = pd.DataFrame()

# for each directory in the search directory
for dir in os.listdir(searchDir):
    # loop through the files in the directory
    # check if the directory is a directory
    if os.path.isdir(searchDir+dir):
        for file in os.listdir(searchDir+dir):
            currDir = searchDir+dir+'/'
            # check filename
            if file == "energyFile.csv":
                filename = currDir+file
                # read the csv file into a dataframe
                header = pd.read_csv(filename,sep='\t',header=None, nrows=1,usecols=range(29)).dropna(axis=1)
                df = pd.read_csv(filename, sep='\t', header=None, skiprows=2, usecols=range(29))
<<<<<<< HEAD
                print(header.iloc[0])
=======
>>>>>>> ad76af7087793a7c3c58fcc8c653ea5605f2b2ff
                df.columns = header.iloc[0]
                # combine the dataframes
                outputDf = pd.concat([outputDf,df],axis=0)

# remove the first column
outputDf.to_csv(searchDir+"/compiledEnergies.csv")