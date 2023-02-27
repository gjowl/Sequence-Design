"""
Will generate a configuration file for analyzeSuccessfulDesignGridPoints.py and generateDesignGeometryGrid.py
"""

import configparser

# create config file object
config_file = configparser.ConfigParser()

# main code config options
programName = 'designGrid'
configFile = programName + '.config' 

# main code section
config_file["main"]={
    "GASrightXStart": 6.5,
    "GASrightCrossStart": -45,
    "rightXStart": 8,
    "rightCrossStart": -45,
    "leftXStart": 8.5,
    "leftCrossStart": 18,
    "xShiftRange": 1,
    "crossingAngleRange": 10,
    "axialRotationRange": 100,
    "zShiftRange": 6,
    "xIncrement": 0.2,
    "crossIncrement": 2,
    "axIncrement": 5,
    "zIncrement": 0.5,
    "numGeometries": 100,
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