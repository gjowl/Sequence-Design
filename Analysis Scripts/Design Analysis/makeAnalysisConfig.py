"""
This script creates a config file for the runDesignAndMakeCHIP.py and all of the scripts that are
run by it. It divides the configuration settings by the script name, allowing for easy access of
the correct portion of the config file by each of the programs.
"""

import configparser

# create config file object
config_file = configparser.ConfigParser()


projectDir = '/data02/gloiseau/Sequence_Design_Project/Design_Data'
dataDir = projectDir + '/12_06_2021_CHIP1_Dataset'
outputDir = projectDir + '/AnalyzedData'
compileDesignDataFile = '/compiledDesignData.csv'
codeDir = '/exports/home/gloiseau/github/Sequence-Design/Analysis Scripts/Design Analysis'

# main code section
config_file["main"]={
    "outputDir":outputDir,
    "codeDir":codeDir,
}

# compileDesignData section
config_file["compileDesignData"]={
    "outputDir":outputDir,
    "dataDir":dataDir,
    "outFile":compileDesignDataFile
}

# analyzeDesignData section
config_file["analyzerConfig"]={
    "outputDir":outputDir,
    "energyLimit":-5,
    "densityLimit":0.7,
    "listAA":["A", "F", "G", "I", "L", "S", "T", "V", "W", "Y"],
    "dataFile":outputDir + compileDesignDataFile,
    "outFile":"/analyzedDesignData.xlsx",
    "kdeFile":"C:\\Users\\gjowl\\Downloads\\2020_09_23_kdeData.csv"#TODO: download this and change path
}

#TODO: I haven't yet decided if I want to run the geomRepack right after from this file. I feel like that would take awhile, so I may split it for now
# BUT I can print out a file that can be used to submit all of those jobs, submit, and then make another version of this for geomRepack analysis?

# SAVE CONFIG FILE
with open(r"analysis.config", 'w') as configfileObj:
    config_file.write(configfileObj)
    configfileObj.flush()
    configfileObj.close()

print("Config file 'analysis.config' created")

# PRINT FILE CONTENT
read_file = open("analysis.config", "r")
content = read_file.read()
print("Content of the config file are:\n")
print(content)
read_file.flush()
read_file.close()
