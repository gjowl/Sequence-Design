# -*- coding: utf-8 -*-
# @Author: Gilbert Loiseau
# @Date:   1969-12-31 18:00:00
# @Last Modified by:   Gilbert Loiseau
# @Last Modified time: 2022-04-22 15:40:07
"""
This script creates a config file for the runDesignAndMakeCHIP.py and all of the scripts that are
run by it. It divides the configuration settings by the script name, allowing for easy access of
the correct portion of the config file by each of the programs.

Taken from: https://www.codeproject.com/Articles/5319621/Configuration-Files-in-Python?msclkid=cd9787d6a70111ec82d314428d9b55e4
"""

import configparser

# create config file object
config_file = configparser.ConfigParser()

# main code config options
programName = 'analyzeDesignsAndRepack'
projectDir = '/data02/gloiseau/Sequence_Design_Project/Design_Data'
datasetToAnalyze = '/12_06_2021_CHIP1_Dataset'
dataDir = projectDir + datasetToAnalyze
outputDir = projectDir + '/AnalyzedData' + datasetToAnalyze
compiledDesignDataFile = dataDir + '/compiledDesignData.csv'
codeDir = '/exports/home/gloiseau/github/Sequence-Design/Analysis_Scripts/analyzeDesignsAndRepack'
analyzeDataScript = codeDir + "/analyzeDesignData.py"
generateSubmitScript = codeDir + "/generateSubmitFile.py"
requirementsFile = codeDir + "/requirements.txt"
energyFileName = "energyFile.csv"
mslDir = "/exports/home/gloiseau/mslib/trunk_AS"
submitDir = mslDir + "/condor"

# main code section
config_file["main"]={
    "outputDir":outputDir,
    "codeDir":codeDir,
    "analyzeDataScript":analyzeDataScript,
    "generateSubmitScript":generateSubmitScript,
    "requirementsFile":requirementsFile,
    "energyFileName":energyFileName,
    "outFile":compiledDesignDataFile,
    "submitDir":submitDir,
    "dataDir":dataDir
}

outFile = outputDir+"/analyzedDesignData.xlsx"
kdeFile = projectDir + '/2020_09_23_kdeData.csv'
variableFile = projectDir + '/repackConfigList.csv'
sequenceProbabilityFile = projectDir + '/sequenceProbabilityFile.csv'
# analyzeDesignData section
config_file["analyzeDesignData"]={
    "outputDir":outputDir,
    "plotOutputDir":outputDir+"/Plots/Design_Plots",
    "energyLimit":-5,
    "densityLimit":0.7,
    "crossingAngleLimit":-70,
    "listAA":"A,F,G,I,L,S,T,V,W,Y",
    "dataFile":compiledDesignDataFile,
    "outFile":outFile,
    "kdeFile":kdeFile,
    "variableFile":variableFile,
    "sequenceProbabilityFile":sequenceProbabilityFile
}

submitFile = "backboneOptimization.condor"
header = "#Submit file for optimizing backbones and making mutants on designed sequences"
batchName = "backboneOptimization"
baseDir = "/data02/gloiseau/Sequence_Design_Project/vdwSequenceDesign/$(batch_name)"
executable = "/exports/home/gloiseau/mslib/trunk_AS/bin/geomRepack"
output = batchName+"/out/$().out"
log = batchName+"/out/$().log"
error = batchName+"/out/$().err"
arguments = "--config $(configFile)"
variables = "sequence,configFile"

# generateSubmitFile section
config_file["generateSubmitFile"]={
    "fileName":projectDir+submitFile,
    "header":header,
    "batchName":batchName,
    "baseDir":baseDir,
    "executable":executable,
    "output":output,
    "log":log,
    "error":error,
    "arguments":arguments,
    "variables":variables,
    "variableFile":variableFile
}

# SAVE CONFIG FILE
with open(programName+".config", 'w+') as configfileObj:
    config_file.write(configfileObj)
    configfileObj.flush()
    configfileObj.close()

print("Config file "+programName+".config created")

# PRINT FILE CONTENT
read_file = open(programName+".config", "r")
content = read_file.read()
print("Content of the config file are:\n")
print(content)
read_file.flush()
read_file.close()
