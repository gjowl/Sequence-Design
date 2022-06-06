"""
Example code for generating a configuration file for ngsAnalysis
"""
import os
import configparser

# create config file object
config_file = configparser.ConfigParser()

# set up directory structure
currDir = os.getcwd()
parentDir = os.path.dirname(currDir)

# input files

# output files

# program files

#ADD CODE HERE

config_file["main"]={

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