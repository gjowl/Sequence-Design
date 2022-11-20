"""
Example code for generating a configuration file for ngsAnalysis
"""
import os
import configparser

# create config file object
config_file = configparser.ConfigParser()
configFile = 'analyzeDesigns.config'

# set up directory structure
currDir = os.getcwd()

# input files
inputDir = currDir + '/inputFiles'
kdeFile = inputDir + '/2020_09_23_kdeData.csv'
seqEntropyFile = inputDir + '/2021_12_05_seqEntropies.csv'
sequenceProbabilitiesFile = inputDir + '/2021_12_05_sequenceProbabilities.csv'
requirementsFile = inputDir + '/requirements.txt'

# input directories
dataDir = '/data02/gloiseau/Sequence_Design_Project/DesignRun2'
#dirToAnalyze = '/2022-11-20_alaNoSeqEntropy'
dirToAnalyze = '/2022-11-20_leuNoSeqEntropy'
#dirToAnalyze = '/2022-11-19_leuEntropyCompare'
#dirToAnalyze = '/2022-11-19_alaEntropyCompare'
rawDataDir = dataDir+dirToAnalyze+'/'

# scripts
scriptDir = currDir + '/code'
compileEnergyScript = scriptDir + '/compileEnergyFiles.py'
designAnalysisScript = scriptDir + '/analyzeDesignData_v3.py'
createPseScript = scriptDir + '/createPymolSessionFiles.py'

# output
outputDir = currDir + dirToAnalyze
dataFile = outputDir + '/compiledData.csv'

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
}

config_file["compileEnergyFiles"]={
    "outputDir": outputDir,
    "rawDataDir": rawDataDir,
    "dataFile": dataFile,
}

numSeqs = 10
config_file["analyzeDesignData"]={
    "kdeFile": kdeFile,
    "seqEntropyFile": seqEntropyFile,
    "sequenceProbabilitiesFile": sequenceProbabilitiesFile,
    "outputDir": outputDir,
    "dataFile": dataFile,
    "numSeqs": numSeqs,
}

config_file["createPseScript"]={
    "outputDir": outputDir,
    "rawDataDir": rawDataDir,
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