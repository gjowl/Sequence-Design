"""
Example code for generating a configuration file for ngsAnalysis
"""
import os
import configparser

# create config file object
config_file = configparser.ConfigParser()
configFile = 'calcEnergyAnalysis_CHIP1_alaEnds.config'

# set up directory structure
currDir = os.getcwd()


# input directories
dataDir = '/data02/gloiseau/Sequence_Design_Project/CHIP1_DesignData'
dirToAnalyze = '2023-2-14_calcEnergyCHIP1_alaEnds'
rawDataDir = f'{dataDir}/{dirToAnalyze}/'

# output
outputDir = f'{currDir}/CHIP1_data_alaEnds'
dataFile = f'{outputDir}/{dirToAnalyze}.csv'
requirementsFile = f'{currDir}/requirements.txt'
toxgreenFile = f'{currDir}/designs_with_energyDiff.csv'

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