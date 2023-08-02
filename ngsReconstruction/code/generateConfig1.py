"""
Will generate a configuration file for ngsAnalysis
"""

import configparser, os

# create config file object
config_file = configparser.ConfigParser()

# set up directory structure
currDir = os.getcwd()

# main code config options
programName = 'ngsAnalysis'
analysisDir = currDir+'/CHIP2/'
#analysisDir = currDir+'/JC_CHIP2/'
codeDir = os.getcwd()+'/code/'
#dataDir = '/data/NGS/'
dataDir = '/home/loiseau@ad.wisc.edu/senesDrive/General/data/data02/gloiseau/2020-2024_Sequence_Design_Project/2023_CHIP2_Data/NGS_fastq/'
#dataDir = '/mnt/d/2023-7-28_NGS_CHIP2/JC_fastq/'
#analysisDir = '/mnt/d/github/Sequence-Design/ngsReconstruction/CHIP1/'
#codeDir = '/mnt/d/github/Sequence-Design/ngsReconstruction/code/'
#dataDir = '/mnt/d/2022-5-13/'
extractionDir = analysisDir + 'data/'
outputDir = analysisDir
inputDir = analysisDir + 'inputFiles/'
analyzedDataDir = analysisDir + 'analyzedData/'
configFile = analysisDir+programName+".config" 

# input files
requirementsFile = inputDir + "requirements.txt"
refFile = inputDir + "refSeqs.csv"
namesFile = inputDir + "dataFilenames.csv"

# output files
countFile = analysisDir+"Count.csv"
percentFile = analysisDir+"Percentage.csv"

# program files
fastqTotxt = codeDir + "fastqToTxt.pl"
ngsAnalysis = codeDir + "ngsAnalysis.py"
energyAnalysis = codeDir + "energyAnalysis.py"

# booleans
analyzeEnergies = False

# main code section
config_file["main"]={
    "programName":programName,
    "extractionDir":extractionDir,
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
reconstructionFile = analyzedDataDir+"reconstructionAllData.csv"
reconstructionFile = analyzedDataDir+"reconstructionAllData.csv"
countDir = analyzedDataDir+"reconstruction_by_count/"
percentDir = analyzedDataDir+"reconstruction_by_percent/"
maltoseTestDir = analyzedDataDir+"maltoseTest/"
maltoseCutoff = -95 #simple cutoff that we've used in the past; also can use negative control values
gpa = 'LIIFGVMAGVIG'
g83i = 'LIIFGVMAIVIG'
gpaFluor = 109804.5
g83iFluor = 39740
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
    "gpaFluor":gpaFluor,
    "g83iFluor":g83iFluor,
    "maltoseTestDir":maltoseTestDir,
    "maltoseCutoff":maltoseCutoff,
}

# energyAnalysis config options
energyFile = inputDir+"chipEnergyFile.csv"
# for now, decided to only continue forward with this data 
# (seems closest to SMA and JC reconstruction)
energyDir = analyzedDataDir+'energyAnalysis/'
# energyAnalysis config
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