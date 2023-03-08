"""
Example code for generating a configuration file for ngsAnalysis
"""
import os
import configparser

# input directories
rootDir = os.getcwd()
dataDir = '/mnt/c/Users/gjowl/Downloads'
#dirToAnalyze = '/2022-11-20_alaNoSeqEntropy'
dirToAnalyze = '2023-3-7_leuDesigns'
#dirToAnalyze = '/2022-11-19_leuEntropyCompare'
#dirToAnalyze = '/2022-11-19_alaEntropyCompare'
rawDataDir = f'{dataDir}/{dirToAnalyze}'
configDir = f'{rootDir}/config'

# make the config directory if it doesn't exist
os.makedirs(configDir, exist_ok=True)

# create config file object
config_file = configparser.ConfigParser()
configFile = f'{configDir}/{dirToAnalyze}.config'

# set up directory structure
currDir = os.getcwd()

# input files
inputDir = f'{currDir}/inputFiles'
kdeFile = f'{inputDir}/2020_09_23_kdeData.csv'
seqEntropyFile = f'{inputDir}/2021_12_05_seqEntropies.csv'
sequenceProbabilitiesFile = f'{inputDir}/2021_12_05_sequenceProbabilities.csv'
requirementsFile = f'{inputDir}/requirements.txt'

# scripts
scriptDir = f'{currDir}/code'
compileEnergyScript = f'{scriptDir}/compileEnergyFiles.py'
designAnalysisScript = f'{scriptDir}/analyzeDesignData.py'
createPseScript = f'{scriptDir}/createPymolSessionFiles.py'

# output
outputDir = f'{currDir}/{dirToAnalyze}'
dataFile = f'{outputDir}/compiledData.csv'
numSeqs = 10

# main code section
config_file["main"]={
    "kdeFile": kdeFile,
    "seqEntropyFile": seqEntropyFile,
    "sequenceProbabilitiesFile": sequenceProbabilitiesFile,
    "requirementsFile": requirementsFile,
    "compileEnergyScript": compileEnergyScript,
    "designAnalysisScript": designAnalysisScript,
    "createPseScript": createPseScript,
    "outputDir": outputDir,
    "rawDataDir": rawDataDir,
    "dataFile": dataFile,
    "numSeqs": numSeqs,
}

# SAVE CONFIG FILE
with open(configFile, 'w+') as configfileObj:
    config_file.write(configfileObj)
    configfileObj.flush()
    configfileObj.close()

print("Config file "+configFile+" created")

# PRINT FILE CONTENT
read_file = open(configFile, "r")
content = read_file.read()
print("Content of the config file are:\n")
print(content)
read_file.flush()
read_file.close()