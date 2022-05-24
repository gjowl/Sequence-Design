import configparser

# create config file object
config_file = configparser.ConfigParser()

# main code config options
programName = 'ngsAnalysis'
analysisDir = '/exports/home/gloiseau/github/Sequence-Design/ngsAnalysis/2022-5-13/'
codeDir = '/exports/home/gloiseau/github/Sequence-Design/ngsAnalysis/code/'
dataDir = '/data/NGS/'
#codeDir = '/mnt/c/Users/gjowl/github/Sequence-Design/ngsAnalysis/2022-5-13/'
#dataDir = '/mnt/d/2022-5-13/'
outputDir = analysisDir + 'data/'
inputDir = analysisDir + 'inputFiles/'
analyzedDataDir = analysisDir + 'analyzedData/'

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