"""
Code for generating a configuration file. Run from the command line with:
$ python3 code/generateConfig.py

This will output the config file to the config folder found in the root directory of the project.
"""
import os
import configparser

# input directories
rootDir = os.getcwd()
dataDir = '/mnt/c/Users/gjowl/Downloads'
inputDirName = 'gblock_native'
rawDataDir = f'{dataDir}/{inputDirName}'
configDir = f'{rootDir}/config'

# make the config directory if it doesn't exist
os.makedirs(configDir, exist_ok=True)

# create config file object
config_file = configparser.ConfigParser()
configFile = f'{configDir}/{inputDirName}.config'

# set up directory structure
currDir = os.getcwd()

# input files
inputDir = f'{currDir}'
requirementsFile = f'{inputDir}/requirements.txt'

# scripts
scriptDir = f'{currDir}/code'
script1 = f'{scriptDir}/untarFolders.py'
script2 = f'{scriptDir}/addPdbsToDir.py'
script3 = f'{scriptDir}/createCalcEnergyCsv.py'
script4 = f'{scriptDir}/deleteExcessInfoFromPDB.py'

# output
outputDir = f'{currDir}/{inputDirName}'
extractionDir = f'{outputDir}/{inputDirName}_extracted'
outputFile = f'{inputDirName}_calcEnergy.csv'
pdbDir = f'{outputDir}/{inputDirName}_pdbs'

# main code section
config_file["main"]={
    "requirementsFile": requirementsFile,
    "inputDir": rawDataDir,
    "untarFolders": script1,
    "addPdbsToDir": script2,
    "createCalcEnergyCsv": script3,
    "deleteExcessInfo": script4,
    "outputDir": outputDir,
    "extractionDir": extractionDir,
    "pdbDir": pdbDir,
    "outputFile": outputFile 
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