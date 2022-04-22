# -*- coding: utf-8 -*-
# @Author: Gilbert Loiseau
# @Date:   2021-12-25
# @Last Modified by:   Gilbert Loiseau
# @Last Modified time: 2022-04-22 15:42:05
"""
This file will run multiple python scripts for analyzing repacked designs and prepare a CHIP to order
"""

import sys
import os
import helper
from utilityFunctions import *

# Use the utilityFunction to get the configFile
configFile = getConfigFile(__file__)

# Use the utilityFunctions function to get the name of this program
programName = getProgramName(sys.argv[0])

# Read in configuration file:
globalConfig = helper.read_config(configFile)
config = globalConfig[programName]

# Config file options:
outputDir            = config["outputDir"]
analysisCodeDir      = config["codeDir"]
energyFileName       = config["energyFileName"]
outFile              = config["outFile"]
requirementsFile     = config["requirementsFile"]
compileDataScript    = config["compileDataScript"]
analyzeDataScript    = config["analyzeDataScript"]
generateSubmitScript = config["generateSubmitScript"]
prepareCHIPScript    = config["prepareCHIPScript"]

if __name__ == '__main__':
    # make the output directory that these will all output to
    makeOutputDir(outputDir)
    #install required packages for the below programs; these are found in requirements.txt
    #if you decide to add more packages to these programs, execute the below and it will update the requirements file:
    #   -pip freeze > requirements.txt
    #tips for requirements files https://pip.pypa.io/en/latest/reference/requirements-file-format/#requirements-file-format
    execInstallRequirements = "pip install -r " + requirementsFile
    os.system(execInstallRequirements)

    # Compiles backbone optimization energy files from all design directories
    executeCompileData = "python3 "+compileDataScript+" "+configFile
    os.system(executeCompileData)
    print("Design energy files compiled")

    # Analyzes backbone optimized designs and outputs a file to generate a CHIP
    executeAnalyzeData = "python3 "+analyzeDataScript+" "+configFile
    os.system(executeAnalyzeData)
    print("Designs analyzed")#TODO: output the number of "successful designs"?

    # Uses the previously analyzed output file to generate a CHIP to order
    executeCHIPScript = "python3 "+prepareCHIPScript+" "+configFile
    os.system(executeCHIPScript)
