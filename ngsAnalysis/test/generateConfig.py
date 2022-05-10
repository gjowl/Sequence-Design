import configparser

# create config file object
config_file = configparser.ConfigParser()

# main code config options
programName = 'ngsAnalysis'
outputDir = '/exports/home/gloiseau/github/Sequence-Design/ngsAnalysis/test/output/'
dataDir = '/data02/jchoi/NGS Submissions/200812/Raw Data/'
codeDir = '/exports/home/gloiseau/github/Sequence-Design/ngsAnalysis/test/'
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
}

# fastqToTxt config options
refFile   = codeDir + "CheatRefSeqs.csv"
gpa = 'LIIFGVMAGVIG'
g83I = 'LIIFGVMAIVIG'
fPrimer = "GGCTCCAAACTTGGGGAATCG"
rPrimer = "CCTGATCAACCCAAGCCAATCC"
outputFile = ''

# fastqToTxt config
config_file["fastqTotxt"]={
    "gpa":gpa,
    "g83I":g83I,
    "fPrimer":fPrimer,
    "rPrimer":rPrimer,
    "refFile":refFile,
    "outputDir":outputDir
}

# compile datafile config options
config_file["compileDataFiles"]={

}

# compile datafile config
# ngsAnalysis config options

compileDataDir = ''
# ngsAnalysis config
config_file["ngsAnalysis"]={
    "dataDir":compileDataDir,
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
