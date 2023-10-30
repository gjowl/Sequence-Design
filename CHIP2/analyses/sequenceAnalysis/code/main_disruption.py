import os, sys, configparser
import pandas as pd

"""

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
codeDir = config['codeDir']
#rawDataDir = config['rawDataDir']
outputDir = config['outputDir']
requirementsFile = config['requirementsFile']
sequenceFile = config['sequenceFile']
mutantFile = config['mutantFile']

# make the output directory if it doesn't exist
if not os.path.exists(outputDir):
    os.makedirs(outputDir)

if __name__ == "__main__":
    # install the requirements
    execInstallRequirements = "pip install -r " + requirementsFile + " | { grep -v 'already satisfied' || :; }" 
    os.system(execInstallRequirements)

    # run the script to add the necessary columns to the dataframes
    execAddColumns = f'python3 {codeDir}/addNecessaryColumns.py {sequenceFile} {mutantFile} {outputDir}'
    os.system(execAddColumns)

    # run the voiding script if the voiding data is found in the config file
    execplotBoxplot = f'python3 {codeDir}/plotBoxplotsPerAAPosition.py {outputDir}/wt.csv {outputDir}/mutant.csv {outputDir}'
    os.system(execplotBoxplot)

    # run boxplot script for all of the data
    execplotBoxplotCombined = f'python3 {codeDir}/plotBoxplotsCombined.py {outputDir}/all.csv {outputDir}/combined'
    os.system(execplotBoxplotCombined)