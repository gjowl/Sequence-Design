# @Author: Gilbert Loiseau
# @Date:   2021-12-25
# @Filename: runDesignAndMakeCHIP.py
# @Last modified by:   Gilbert Loiseau
# @Last modified time: 2022/03/21

"""
This file will run multiple python scripts for compiling ngs data and then analyzing.
"""

from fileinput import filename
import sys
import os
import helper
import pandas as pd
from functions import *

#FUNCTIONS
# gets a list of all of the unique sequences present in data within a directory
def outputGoodSequenceDataframe(dir):
    listSeq = []
    listId = []
    for file in os.listdir(dir):
        dataFile = os.path.join(dir, file)
        # the below helps read csv files with differing numbers of columns: 
        # https://stackoverflow.com/questions/27020216/import-csv-with-different-number-of-columns-per-row-using-pandas
        # Delimiter
        delim = '\t'
        # The max column count a line in the file could have
        largest_column_count = 0
        # Loop the data lines
        with open(dataFile, 'r') as temp_f:
            # Read the lines
            lines = temp_f.readlines()
            for l in lines:
                # Count the column count for the current line
                column_count = len(l.split(delim)) + 1
                # Set the new most column count
                largest_column_count = column_count if largest_column_count < column_count else largest_column_count
        colName = file[6:13]
        # Generate column names (will be 0, 1, 2, ..., largest_column_count - 1)
        column_names = [i for i in range(0, largest_column_count)]
        dfData = pd.read_csv(dataFile, delimiter=delim, header=None, skiprows=3, names=column_names)
        dfData = dfData[dfData.iloc[:,3] != 'Unknown']
        numColumns = len(dfData.columns)
        dfData.insert(numColumns, "Replicate", colName)
        listSeq.extend(dfData.iloc[:,0].tolist())
        listId.extend(dfData.iloc[:,4].tolist())
    df = pd.DataFrame(list(zip(listSeq,listId)), columns=['Sequence','Id'] )
    return df
    #dfOut.drop_duplicates(subset=[0], keep=False, inplace=True)

def addInUniprotIds(df, outputDir, file):
    outputFile = outputDir+"allCounts_withIds.csv" 
    fileExists = check_file_empty(outputFile)
    if fileExists == False:
        dfOut = pd.DataFrame()
        dfData = pd.read_csv(file, delimiter=',', index_col=0)
        idList = []
        # checking if file exist and it is empty
        for seq, row in dfData.iterrows():
            index = df.index[df['Sequence'] == seq].to_list()[0]
            id = df.loc[index, 'Id']
            idList.append(id)
        numCol = len(dfData.columns)
        dfOut = dfData
        dfOut.insert(0, "Ids", idList)
        outputFile = outputDir+"allCounts_withIds.csv" 
        dfOut.to_csv(outputFile)
    else:
        print("File with uniprot ids exists. To remake", file)

# Use the utilityFunction to get the configFile
configFile = getConfigFile(__file__)

# Use the utilityFunctions function to get the name of this program
programName = getFilename(sys.argv[0])

# Read in configuration file:
globalConfig = helper.read_config(configFile)
config = globalConfig[programName]

# Config file options:
outputDir            = config["outputDir"]
requirementsFile     = config["requirementsFile"]
dataDir              = config["dataDir"]
testDir              = config["testDir"]
fastqTotxt           = config["fastqTotxt"]
ngsAnalysis          = config["ngsAnalysis"]
outFile              = config["outputFile"]

if __name__ == '__main__':
    # make the output directory that these will all output to
    makeOutputDir(outputDir)
    #install required packages for the below programs; these are found in requirements.txt
    #if you decide to add more packages to these programs, execute the below and it will update the requirements file:
    #   -pip freeze > requirements.txt
    #tips for requirements files:
    #  https://pip.pypa.io/en/latest/reference/requirements-file-format/#requirements-file-format
    #  gets rid of requirement output: https://github.com/pypa/pip/issues/5900?msclkid=474dd7c0c72911ec8bf671f1ae3975f0
    execInstallRequirements = "pip install -r " + requirementsFile + " | { grep -v 'already satisfied' || :; }" 
    os.system(execInstallRequirements)

    # runs through all files in the dataDir and converts fastq to txt; only runs if no files are found in the output dir
    convertFastqToTxt(fastqTotxt, configFile, dataDir, outputDir)
    
    # get list of sequences
    seqIdDf = outputGoodSequenceDataframe(outputDir)
    # get the sequence column (first column) and skip the summary data rows
    seqColumn = seqIdDf.iloc[:,0].tolist()
    ## add each value in the list to the allSeqs list
    #for seq in seqColumn:
    #    allSeqs.append(seq) 
    #for id in idColumn:
    #    allIds.append(id) 
    ## rid of the duplicate sequences in the list
    #allSeqs = pd.unique(allSeqs).tolist()
    #allIds = pd.unique(allIds).tolist()

    # make csv with sequence counts for all files
    # go through all files and save counts in dictionary
    outputSequenceCountsCsv(seqColumn, outputDir, outFile)
    seqIdDf = seqIdDf.drop_duplicates(subset='Sequence', keep='first')
    seqIdDf = seqIdDf.reset_index(drop=True)
    #dfOut.drop_duplicates(subset=[0], keep=False, inplace=True)
    addInUniprotIds(seqIdDf, testDir, outFile)

    # execute ngsAnalysis script 
    execNgsAnalysis = 'python3 '+ngsAnalysis+' '+configFile
    os.system(execNgsAnalysis)

    
