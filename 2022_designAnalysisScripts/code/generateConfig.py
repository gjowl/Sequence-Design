"""
Example code for generating a configuration file for ngsAnalysis
"""
import os
import configparser

# create config file object
config_file = configparser.ConfigParser()

# set up directory structure
currDir = os.getcwd()

# main code config options
programName = 'designAnalysis'

# input files
kdeFile = currDir + '/2020_09_23_kdeData.csv'
seqEntropyFile = currDir + '/2021_12_05_seqEntropies.csv'
sequenceProbabilitiesFile = currDir + '/2021_12_05_sequenceProbabilities.csv'

# main code section
config_file["main"]={
    "programName": programName,
    "kdeFile": kdeFile,
    "seqEntropyFile": seqEntropyFile,
    "sequenceProbabilitiesFile": sequenceProbabilitiesFile
}

# SAVE CONFIG FILE
with open(configFile, 'w+') as configfileObj:
    config_file.write(configfileObj)
    configfileObj.flush()
    configfileObj.close()

print("Config file "+programName+".config created")

# PRINT FILE CONTENT
read_file = open(configFile, "r")
content = read_file.read()
print("Content of the config file are:\n")
print(content)
read_file.flush()
read_file.close()