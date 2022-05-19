import configparser

# create config file object
config_file = configparser.ConfigParser()

# main code config options
programName = 'ngsAnalysis'
codeDir = '/exports/home/gloiseau/github/Sequence-Design/ngsAnalysis/2022-5-13/'
dataDir = '/data/NGS/'
#codeDir = '/mnt/c/Users/gjowl/github/Sequence-Design/ngsAnalysis/2022-5-13/'
#dataDir = '/mnt/d/2022-5-13/'
outputDir = codeDir + 'data/'
inputDir = codeDir + 'inputFiles/'
analysisDir = codeDir + 'analyzedData/'

# input files
requirementsFile = inputDir + "requirements.txt"
refFile = inputDir + "refSeqs.csv"

# output files
countFile = inputDir+"allCounts.csv"
percentFile = inputDir+"allPercents.csv"

# program files
fastqTotxt = codeDir + "fastqTotxt.py"
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
}

# fastqToTxt config options
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
}

# ngsAnalysis config options
flowFile = inputDir+"flowFile.csv"
# ngsAnalysis config
config_file["ngsAnalysis"]={
    "inputDir":outputDir,
    "outputDir":analysisDir,
    "countFile":countFile,
    "percentFile":percentFile,
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