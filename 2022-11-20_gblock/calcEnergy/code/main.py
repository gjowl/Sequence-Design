import os, sys, configparser
import pandas as pd

"""
Code for compiling energyFile.csv files from an input directory and analyzing the data
"""
# Helper file for reading the config file of interest for running the program
def read_config(configFile):
    config = configparser.ConfigParser()
    config.read(configFile)
    return config

# get the current directory
cwd = os.getcwd()

# get the config file options
configFile = sys.argv[1]
globalConfig = read_config(configFile)
config = globalConfig['main']

# read in the config arguments
rawDataDir = config['rawDataDir']
outputDir = config['outputDir']
dataFile = config['dataFile']
requirementsFile = config['requirementsFile']
toxgreenFile = config['toxgreenFile']

# make the output directory if it doesn't exist
if not os.path.exists(outputDir):
    os.makedirs(outputDir)

if __name__ == "__main__":
    # install the requirements
    execInstallRequirements = "pip install -r " + requirementsFile + " | { grep -v 'already satisfied' || :; }" 
    os.system(execInstallRequirements)

    # compile the energy files
    os.system(f'python3 {cwd}/code/compileEnergyFiles.py {rawDataDir} {dataFile}') 

    # add the percent gpa to the dataframe
    # get the dataFile name without the extension
    dataFilename = os.path.splitext(dataFile)[0]
    outputFile = f'{dataFilename}_percentGpa.csv'
    os.system(f'python3 {cwd}/code/addPercentGpaToDf.py {dataFile} {toxgreenFile} {outputFile}')

    # analyze the data
    os.system(f'python3 {cwd}/code/analyzeData.py {outputFile} {outputDir}')