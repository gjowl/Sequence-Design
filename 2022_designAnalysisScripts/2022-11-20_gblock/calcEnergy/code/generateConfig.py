"""
Example code for generating a configuration file for ngsAnalysis
"""
import os
import configparser

# create config file object
config_file = configparser.ConfigParser()
configFile = 'calcEnergyAnalysis_normalSeqs.config'

# set up directory structure
currDir = os.getcwd()


# input directories
dataDir = '/mnt/c/Users/gjowl/Downloads'
dirToAnalyze = '2023-2-7_calcEnergy_normalSeqs'
rawDataDir = f'{dataDir}/{dirToAnalyze}/'

# output
outputDir = f'{currDir}/data_originalGblockSeqs'
dataFile = f'{outputDir}/{dirToAnalyze}.csv'
requirementsFile = f'{currDir}/requirements.txt'
toxgreenFile = f'{currDir}/data/toxgreen.csv'

# main code section
config_file["main"]={
    "outputDir": outputDir,
    "rawDataDir": rawDataDir,
    "dataFile": dataFile,
    "toxgreenFile": toxgreenFile,
    "requirementsFile": requirementsFile
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