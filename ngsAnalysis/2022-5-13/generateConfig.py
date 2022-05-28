"""
Will generate a configuration file for ngsAnalysis
"""

import configparser

# create config file object
config_file = configparser.ConfigParser()

# main code config options
programName = 'ngsAnalysis'
#analysisDir = '/exports/home/gloiseau/github/Sequence-Design/ngsAnalysis/2022-5-13/'
#codeDir = '/exports/home/gloiseau/github/Sequence-Design/ngsAnalysis/code/'
#dataDir = '/data/NGS/'
analysisDir = '/mnt/c/Users/gjowl/github/Sequence-Design/ngsAnalysis/2022-5-13/'
codeDir = '/mnt/c/Users/gjowl/github/Sequence-Design/ngsAnalysis/code/'
dataDir = '/mnt/d/2022-5-13/'
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
energyAnalysis = codeDir + "energyAnalysis.py"

# booleans
analyzeEnergies = True

# main code section
config_file["main"]={
    "programName":programName,
    "outputDir":outputDir,
    "dataDir":dataDir,
    "requirementsFile":requirementsFile,
    "fastqTotxt":fastqTotxt,
    "ngsAnalysis":ngsAnalysis,
    "energyAnalysis":energyAnalysis,
    "analyzeEnergies":analyzeEnergies,
    "percentFile":percentFile,
    "countFile":countFile,
    "refFile":refFile,
    "namesFile":namesFile,
}

# ngsAnalysis config options
flowFile = inputDir+"flowFile.csv"
reconstructionFile = analyzedDataDir+"reconstructionFile.csv"
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
    "reconstructionFile":reconstructionFile,
    "countDir":countDir,
    "percentDir":percentDir,
    "maltoseTestDir":maltoseTestDir,
}

# energyAnalysis config options
energyFile = inputDir+"chipEnergyFile.csv"
# for now, decided to only continue forward with this data 
# (seems closest to SMA and JC reconstruction)
energyDir = analyzedDataDir+'energyAnalysis/'
# ngsAnalysis config
config_file["energyAnalysis"]={
    "outputDir":energyDir,
    "energyFile":energyFile,
    "reconstructionFile":reconstructionFile,
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