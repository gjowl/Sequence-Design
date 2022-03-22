"""
This script creates a config file for the runDesignAndMakeCHIP.py and all of the scripts that are
run by it. It divides the configuration settings by the script name, allowing for easy access of
the correct portion of the config file by each of the programs.

taken from: https://www.codeproject.com/Articles/5319621/Configuration-Files-in-Python?msclkid=cd9787d6a70111ec82d314428d9b55e4
"""

import configparser

# create config file object
config_file = configparser.ConfigParser()

#is it possible to automate this in case I do switch the name of the program?
programName = 'analyzeAndRepackDesigns'
projectDir = '/data02/gloiseau/Sequence_Design_Project/Design_Data'
dataDir = projectDir + '/12_06_2021_CHIP1_Dataset'
outputDir = projectDir + '/AnalyzedData'
compiledDesignDataFile = '/compiledDesignData.csv'
codeDir = '/exports/home/gloiseau/github/Sequence-Design/Analysis_Scripts/Design_Analysis'
compileDataScript = codeDir + "/compileAllDesignEnergyFiles.py"
analyzeDataScript = codeDir + "/analyzeDesignData.py"
requirementsFile = codeDir + "/requirements.txt"

# main code section
config_file["main"]={
    "outputDir":outputDir,
    "codeDir":codeDir,
    "compileDataScript":compileDataScript,
    "analyzeDataScript":analyzeDataScript,
    "requirementsFile":requirementsFile
}

# compileDesignData section
config_file["compileAllDesignEnergyFiles"]={
    "outputDir":outputDir,
    "dataDir":dataDir,
    "outFile":compiledDesignDataFile
}

# analyzeDesignData section
config_file["analyzeDesignData"]={
    "outputDir":outputDir,
    "energyLimit":-5,
    "densityLimit":0.7,
    "listAA":["A", "F", "G", "I", "L", "S", "T", "V", "W", "Y"],
    "dataFile":outputDir + compiledDesignDataFile,
    "outFile":"/analyzedDesignData.xlsx",
    "kdeFile":"C:\\Users\\gjowl\\Downloads\\2020_09_23_kdeData.csv"#TODO: download this and change path
}

#TODO: I haven't yet decided if I want to run the geomRepack right after from this file. I feel like that would take awhile, so I may split it for now
# BUT I can print out a file that can be used to submit all of those jobs, submit, and then make another version of this for geomRepack analysis?

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
