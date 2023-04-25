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
convertScoreScript = config['convertScoreScript']
analyzeScoreScript = config['analyzeScoreScript']
outputDir = config['outputDir']
scoreDir = config['scoreDir']
analysisDir = config['analysisDir']
dataFile = config['dataFile']
numSeqs = config['numSeqs']

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
    execExtractScore = f'python3 {extractScoreScript} {outputDir} {scoreDir}'
    os.system(execExtractScore)

    # execute analyze score script for each score file
    for scoreFile in os.listdir(scoreDir):
        # check if the extension is .sc
        if not scoreFile.endswith('.sc'):
            continue
        else:
            # convert score files to csv
            execConvertScore = f'python3 {convertScoreScript} {scoreDir}/{scoreFile} {scoreDir}'
            os.system(execConvertScore)
            # delete the extracted score file (copied from the original directory)
            os.remove(f'{scoreDir}/{scoreFile}')

    for scoreFile in os.listdir(scoreDir):
        # analyze the score file that is now in csv format
        execAnalyzeScore = f'python3 {analyzeScoreScript} {scoreDir}/{scoreFile} {analysisDir}'
        os.system(execAnalyzeScore)
        exit(0)