import configparser

# create config file object
config_file = configparser.ConfigParser()

# main code config options
programName = 'ngsAnalysis'
codeDir = '/exports/home/gloiseau/github/Sequence-Design/ngsAnalysis/2022-5-13/'
#codeDir = '/mnt/c/Users/gjowl/github/Sequence-Design/ngsAnalysis/2022-5-13/'
outputDir = codeDir + 'output/'
testDir = codeDir
outputFile = testDir+"allCounts.csv"
flowFile = testDir+"flowFile.csv"

#dataDir = '/mnt/d/2022-5-13/'
dataDir = '/data/NGS/'

fastqTotxt = codeDir + "fastqTotxt.py"
ngsAnalysis = codeDir + "ngsAnalysis.py"
requirementsFile = codeDir + "requirements.txt"

# main code section
config_file["main"]={
    "outputDir":outputDir,
    "dataDir":dataDir,
    "requirementsFile":requirementsFile,
    "fastqTotxt":fastqTotxt,
    "ngsAnalysis":ngsAnalysis,
    "testDir":testDir,
    "outputFile":outputFile,
}

# fastqToTxt config options
refFile   = codeDir + "refSeqs.csv"
gpa = 'LIIFGVMAGVIG'
g83I = 'LIIFGVMAIVIG'
fPrimer = "GGCTCCAAACTTGGGGAATCG"
rPrimer = "CCTGATCAACCCAAGCCAATCC"

# fastqToTxt config
config_file["fastqTotxt"]={
    "gpa":gpa,
    "g83I":g83I,
    "fPrimer":fPrimer,
    "rPrimer":rPrimer,
    "refFile":refFile,
    "outputDir":outputDir,
    "outputFile":outputFile,
}

# ngsAnalysis config options
compileDataDir = ''

analysisDir = codeDir + 'analyzedData/'
# ngsAnalysis config
config_file["ngsAnalysis"]={
    "inputDir":testDir,
    "outputDir":analysisDir,
    "countFile":outputFile,
    "flowFile":flowFile,
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
