import os
import sys
import configparser
import pandas as pd

# Method to read config file settings
# Helper file for reading the config file of interest for running the program
def read_config(configFile):
    config = configparser.ConfigParser()
    config.read(configFile)
    return config

# get the configuration file for the current
def getConfigFile(configDir):
    configFile = ''
    # Access the configuration file for this program (should only be one in the directory)
    programDir = os.path.realpath(configDir)
    fileList = os.listdir(programDir)
    for file in fileList:
        fileName, fileExt = os.path.splitext(file)
        if fileExt == '.config':
            configFile = programDir + '/' + file
    if configFile == '':
        sys.exit("No config file present in script directory!")
    return configFile

# get filename separate from type and directory
def getFilename(file):
    programPath = os.path.realpath(file)
    programDir, programFile = os.path.split(programPath)
    filename, programExt = os.path.splitext(programFile)
    return filename

# make an output directory if it doesn't exist
def makeOutputDir(outputDir):
    # check if the path to the directory exists
    if not os.path.isdir(outputDir):
        print('Creating output directory: ' + outputDir + '.')
        # the below makes directories for the entire path
        os.makedirs(outputDir)
    else:
        print('Output Directory: ' + outputDir + ' exists.')

# insert column at the end of the dataframe
def insertAtEndOfDf(df, colName, col):
    numCol = len(df.columns)
    df.insert(numCol, colName, col)
    return df
