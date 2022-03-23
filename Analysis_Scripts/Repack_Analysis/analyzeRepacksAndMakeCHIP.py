# @Author: Gilbert Loiseau
# @Date:   2021-12-25
# @Filename: runDesignAndMakeCHIP.py
# @Last modified by:   Gilbert Loiseau
# @Last modified time: 2022/03/22

"""
This file will run multiple python scripts for analyzing repacked designs and prepare a CHIP to order
"""

import os
import helper

from utilityFunctions import *

# Variables
configFile = getConfigFile()
print('Config:',configFile)

if __name__ == '__main__':
    #read in the config file
    config = helper.read_config()

    # make the output directory that these will all output to
    outputDir = config["main"]["outputDir"]
    analysisCodeDir = config["main"]["codeDir"]
    if not os.path.isdir(outputDir):
        print('Creating output directory: ' + outputDir + '.')
        os.mkdir(outputDir)
    else:
        print('Output Directory: ' + outputDir + ' exists.')
    # download the required packages for these programs, list of which is found in requirements.txt
    #exec(python -m pip install -r requirementsFile)

    #install required packages for the below programs; these are found in requirements.txt
    #if you decide to add more packages to these programs, execute the below and it will update the requirements file:
    #   -pip freeze > requirements.txt
    #tips for requirements files https://pip.pypa.io/en/latest/reference/requirements-file-format/#requirements-file-format
    requirementsFile = config["main"]["requirementsFile"]
    execInstallRequirements = "pip install -r "+requirementsFile
    os.system(execInstallRequirements)

#TODO: copied these from the design_analysis, make sure they work properly
    # Compiles backbone optimization energy files from all design directories
    compileDataScript = config["main"]["compileDataScript"]
    executeCompileData = "python3 "+compileDataScript+" "+configFile
    os.system(executeCompileData)
    print("Design energy files compiled")

    # Analyzes backbone optimized designs and outputs a file to generate a CHIP
    analyzeDataScript = config["main"]["analyzeDataScript"]
    executeAnalyzeData = "python3 "+analyzeDataScript+" "+configFile
    os.system(executeAnalyzeData)
    print("Designs analyzed")#TODO: output the number of "successful designs"?

    prepareCHIPScript = config["main"]["prepareCHIPScript"]
    executeCHIPScript = "python3 "+prepareCHIPScript+" "+configFile
    os.system(executeCHIPScript)
