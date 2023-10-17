'''
File: d:\github\Sequence-Design\CHIP2\analyses\figureMaking\code\main.py
Project: d:\github\Sequence-Design\CHIP2\analyses\figureMaking\code
Created Date: Saturday October 7th 2023
Author: gjowl
-----
Last Modified: Saturday October 7th 2023 12:42:41 pm
Modified By: gjowl
-----
Description:

-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------
'''

import os, sys, configparser

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
rawDataDirAla = config['rawDataDirAla'] # where the pdbs for the sequences are located
rawDataDirLeu = config['rawDataDirLeu'] # where the pdbs for the sequences are located
optimizedPdbDir = config['optimizedPdbDir'] # where the pdbs for the sequences are located
outputDir = config['outputDir']
outputFile = config['outputFile']
dataFile = config['dataFile'] # file with the raw data information, including the directory of the pdb files for each sequence
sequenceFile = config['sequenceFile'] # file with the sequences of interest
interfaceFile = config['interfaceFile'] # file with the correct interfaces for each sequence
requirementsFile = config['requirementsFile']

if __name__ == '__main__':
    # install the requirements
    execInstallRequirements = "pip install -r " + requirementsFile + " | { grep -v 'already satisfied' || :; }" 
    os.system(execInstallRequirements)

    # merge the dataframes
    execMergeData = f'python3 {codeDir}/mergeDf_cpsf.py {sequenceFile} {dataFile} {outputFile} {outputDir}'
    os.system(execMergeData)

    # replace the interface column
    execReplaceInterface = f'python3 {codeDir}/replaceInterfaceColumn.py {interfaceFile} {outputDir}/{outputFile}.csv {outputFile} {outputDir}'
    os.system(execReplaceInterface)

    # split into leu and ala designs
    execSplitDesigns = f'python3 {codeDir}/splitDesigns.py {outputDir}/{outputFile}.csv {outputFile} {outputDir}'
    os.system(execSplitDesigns)

    # make the interface pdbs figures
    execCreatePses = f'python3 {codeDir}/createPymolSessionFiles.py {rawDataDirAla} {optimizedPdbDir} {outputDir}/{outputFile}_ala.csv {outputDir}/interfacePdbs'
    os.system(execCreatePses)
    execCreatePses = f'python3 {codeDir}/createPymolSessionFiles.py {rawDataDirLeu} {optimizedPdbDir} {outputDir}/{outputFile}_leu.csv {outputDir}/interfacePdbs'
    os.system(execCreatePses)