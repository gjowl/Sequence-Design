"""
Example code for generating a configuration file for ngsAnalysis
"""
import os
import configparser

# create config file object
config_file = configparser.ConfigParser()

# set up directory structure
currDir = os.getcwd()
#parentDir = os.path.dirname(currDir)

# main code config options
programName = 'ngsAnalysis'
analysisDir = currDir+'/CHIP1/'
codeDir = os.getcwd()+'/code/'
dataDir = '/data/NGS/'
#dataDir = '/mnt/d/2022-5-13/'
outputDir = analysisDir + 'data/'
inputDir = analysisDir + 'inputFiles/'
analyzedDataDir = analysisDir + 'analyzedData/'
configFile = analysisDir+programName+".config" 

# input files
requirementsFile = inputDir + "requirements.txt"
refFile = inputDir + "refSeqs.csv"
namesFile = inputDir + "dataFilenames.csv"

# output files
countFile = inputDir+"allCounts.csv"
percentFile = inputDir+"allPercents.csv"

# program files
fastqTotxt = codeDir + "fastqTotxt.pl"
ngsAnalysis = codeDir + "ngsAnalysis.py"

# main code section
config_file["main"]={
    "programName":programName,
    "outputDir":outputDir,
    "dataDir":dataDir,
    "requirementsFile":requirementsFile,
    "fastqTotxt":fastqTotxt,
    "ngsAnalysis":ngsAnalysis,
    "percentFile":percentFile,
    "countFile":countFile,
    "refFile":refFile,
    "namesFile":namesFile,
}

# ngsAnalysis config options
flowFile = inputDir+"flowFile.csv"
energyFile = inputDir+"chipEnergyFile.csv"
countDir = analyzedDataDir+"reconstruction_by_count/"
percentDir = analyzedDataDir+"reconstruction_by_percent/"
maltoseTestDir = analyzedDataDir+"maltoseTest/"
gpa = 'LIIFGVMAGVIG'
g83I = 'LIIFGVMAIVIG'
# ngsAnalysis config
config_file["ngsAnalysis"]={
    "inputDir":outputDir,
    "outputDir":analyzedDataDir,
    "countFile":countFile,
    "percentFile":percentFile,
    "flowFile":flowFile,
    "energyFile":energyFile,
    "countDir":countDir,
    "percentDir":percentDir,
    "maltoseTestDir":maltoseTestDir,
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