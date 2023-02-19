"""
Example code for generating a configuration file for ngsAnalysis
"""
import os
import configparser

# input directories
#dataDir = '/data02/gloiseau/Sequence_Design_Project/DesignRun2'
dataDir = '/mnt/c/Users/gjowl/Downloads'
inputDirName = '2023-2-14_alaDesigns'
rawDataDir = f'{dataDir}/{inputDirName}'

# create config file object
config_file = configparser.ConfigParser()
configFile = f'{inputDirName}.config'

# set up directory structure
currDir = os.getcwd()

# input files
inputDir = f'{currDir}/inputFiles'
requirementsFile = f'{inputDir}/requirements.txt'

# scripts
scriptDir = f'{currDir}/code'
script1 = f'{scriptDir}/untarFolders.py'
script2 = f'{scriptDir}/addPdbsToDir.py'
script3 = f'{scriptDir}/createCalcEnergyCsv.py'

# output
outputDir = f'{currDir}/{inputDirName}'

# main code section
config_file["main"]={
    "requirementsFile": requirementsFile,
    "untarFolder": script1,
    "addPdbsToDir": script2,
    "createCalcEnergyCsv": script3,
    "outputDir": outputDir,
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