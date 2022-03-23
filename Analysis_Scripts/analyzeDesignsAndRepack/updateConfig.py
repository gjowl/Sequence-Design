"""
This script can be used to update the config file with specific options, rather than having to change them
in generateConfig.py and regenerate the configuration file.

Taken from: https://www.codeproject.com/Articles/5319621/Configuration-Files-in-Python?msclkid=cd9787d6a70111ec82d314428d9b55e4
"""

import configparser
from utilityFunctions import *

# CREATE OBJECT
config_file = configparser.ConfigParser()

# use utilityFunctions to get the config file from this directory
config = getConfigFile(__file__)

# READ CONFIG FILE
config_file.read(config)

# UPDATE A FIELD VALUE
config_file["main"]["outputDir"]="changed_dir"

# ADD A NEW FIELD UNDER A SECTION
config_file["main"].update({"Format":"example new field"})

# SAVE THE SETTINGS TO THE FILE
with open(config,"w+") as file_object:
    config_file.write(file_object)

# DISPLAY UPDATED SAVED SETTINGS
print("Config file ",config," is updated")
print("Updated file settings are:\n")
file=open(config,"r")
settings=file.read()
print(settings)
