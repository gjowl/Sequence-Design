# @Author: Gilbert Loiseau
# @Date:   2021-12-25
# @Filename: runDesignAndMakeCHIP.py
# @Last modified by:   Gilbert Loiseau
# @Last modified time: 2022/03/21

"""
This file will run multiple python scripts for compiling and then analyzing design data.
"""

import sys
import os
import helper
import configparser
from utilityFunctions import *

# Variables
configFile = getConfigFile()
print('Config:',configFile)

if __name__ == '__main__':
    #read in the config file
    config = helper.read_config(configFile)

    # make the output directory that these will all output to
    outputDir = config["main"]["outputDir"]
    analysisCodeDir = config["main"]["codeDir"]

    if not os.path.isdir(outputDir):
        print('Creating output directory: ' + outputDir + '.')
        os.mkdir(outputDir)
    else:
        print('Output Directory: ' + outputDir + ' exists.')

    #install required packages for the below programs; these are found in requirements.txt
    #if you decide to add more packages to these programs, execute the below and it will update the requirements file:
    #   -pip freeze > requirements.txt
    #tips for requirements files https://pip.pypa.io/en/latest/reference/requirements-file-format/#requirements-file-format
    requirementsFile = config["main"]["requirementsFile"]
    execInstallRequirements = "pip install -r "+requirementsFile
    os.system(execInstallRequirements)

    # Compiles design energy files from all design directories
    compileDataScript = config["main"]["compileDataScript"]
    executeCompileData = "python3 "+compileDataScript+" "+configFile
    os.system(executeCompileData)
    print("Design energy files compiled")

    # Analyzes designs and outputs a submit file filled with sequences for backboneOptimization
    analyzeDataScript = config["main"]["analyzeDataScript"]
    executeAnalyzeData = "python3 "+analyzeDataScript+" "+configFile
    os.system(executeAnalyzeData)
    print("Designs analyzed")#TODO: output the number of "successful designs"?
    #TODO: do I also add in a way to run the next step here? I'll need to assume that these files are all found in the same directory
    #os.system("condor_submit backboneOptimization.condor")
