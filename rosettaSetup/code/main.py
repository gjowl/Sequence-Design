import os, sys, pandas as pd
import configparser

"""

"""

# Helper file for reading the config file of interest for running the program
def read_config(configFile):
    config = configparser.ConfigParser()
    config.read(configFile)
    return config

# read in the config file
configFile = sys.argv[1]
globalConfig = read_config(configFile)
config = globalConfig['main']

# read in the config arguments
kdeFile = config['kdeFile']
seqEntropyFile = config['seqEntropyFile']
sequenceProbabilitiesFile = config['sequenceProbabilitiesFile']
rawDataDir = config['rawDataDir']
requirementsFile = config['requirementsFile']
untarFoldersScript = config['untarFoldersScript']
extractScoreScript = config['extractScoreScript']
analyzeScoreScript = config['analyzeScoreScript']
outputDir = config['outputDir']
dataFile = config['dataFile']
numSeqs = config['numSeqs']

# check if the output directory exists
os.makedirs(name=outputDir, exist_ok=True)

if __name__ == '__main__':
    #install required packages for the below programs; these are found in requirements.txt
    #if you decide to add more packages to these programs, execute the below and it will update the requirements file:
    #   -pip freeze > requirements.txt
    #tips for requirements files:
    #  https://pip.pypa.io/en/latest/reference/requirements-file-format/#requirements-file-format
    #  gets rid of requirement output: https://github.com/pypa/pip/issues/5900?msclkid=474dd7c0c72911ec8bf671f1ae3975f0
    execInstallRequirements = "pip install -r " + requirementsFile + " | { grep -v 'already satisfied' || :; }" 
    os.system(execInstallRequirements)
    
    # execute untar folders script 
    execUntar = f'python3 {untarFoldersScript} {rawDataDir} {outputDir}'
    os.system(execUntar)

    # execute extract score script 
    execExtractScore = f'python3 {extractScoreScript} {outputDir}'
    os.system(execExtractScore)

    # execute analyze score script
    execAnalyzeScore = f'python3 {analyzeScoreScript} {rawDataDir} {outputDir}'
    os.system(execAnalyzeScore)