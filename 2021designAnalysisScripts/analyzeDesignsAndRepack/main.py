# @Author: Gilbert Loiseau
# @Date:   2021-12-25
# @Filename: runDesignAndMakeCHIP.py
# @Last modified by:   Gilbert Loiseau
# @Last modified time: 2022/03/21

"""
This file will run multiple python scripts for compiling and then analyzing design data.

TODO: add more here: this runs on a linux machine with condor installed..., website for condor,...
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
analyzeDataScript    = config["analyzeDataScript"]
generateSubmitScript = config["generateSubmitScript"]
dataDir              = config["dataDir"]

#TODO: add in error checking?
if __name__ == '__main__':
    # make the output directory that these will all output to
    makeOutputDir(outputDir)
    #install required packages for the below programs; these are found in requirements.txt
    #if you decide to add more packages to these programs, execute the below and it will update the requirements file:
    #   -pip freeze > requirements.txt
    #tips for requirements files:
    #  https://pip.pypa.io/en/latest/reference/requirements-file-format/#requirements-file-format
    #  gets rid of requirement output: https://github.com/pypa/pip/issues/5900?msclkid=474dd7c0c72911ec8bf671f1ae3975f0
    execInstallRequirements = "pip install -r " + requirementsFile + " | { grep -v 'already satisfied' || :; }" 
    os.system(execInstallRequirements)

    # Compiles design energy files from all design directories
    compileDataFiles(energyFileName, dataDir, outFile)

    # Analyzes designs and outputs a submit file filled with sequences for backboneOptimization
    execAnalyzeData = "python3 " + analyzeDataScript + " " + configFile
    os.system(execAnalyzeData)

    execMakeSubmit = "python3 " + generateSubmitScript + " " + configFile
    os.system(execMakeSubmit)
    
    #execRunRepack = "condor_submit " + mslDir + "/" + ...
    #TODO: do I also add in a way to run the next step here? I'll need to assume that these files are all found in the same directory
    #os.system("condor_submit backboneOptimization.condor")
