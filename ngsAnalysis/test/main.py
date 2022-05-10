# @Author: Gilbert Loiseau
# @Date:   2021-12-25
# @Filename: runDesignAndMakeCHIP.py
# @Last modified by:   Gilbert Loiseau
# @Last modified time: 2022/03/21

"""
This file will run multiple python scripts for compiling ngs data and then analyzing.
"""

import sys
import os
import helper
from functions import *

# Use the utilityFunction to get the configFile
configFile = getConfigFile(__file__)

# Use the utilityFunctions function to get the name of this program
programName = getFilename(sys.argv[0])

# Read in configuration file:
globalConfig = helper.read_config(configFile)
config = globalConfig[programName]

# Config file options:
outputDir            = config["outputDir"]
requirementsFile     = config["requirementsFile"]
dataDir              = config["dataDir"]
fastqTotxt           = config["fastqTotxt"]
ngsAnalysis          = config["ngsAnalysis"]

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

    for filename in os.listdir(dataDir):
        dataFile = os.path.join(dataDir, filename)
        if os.path.isfile(dataFile):
            print(dataFile)
            dataFile = dataFile.replace(" ", "\ ") # replaces spaces so that directories with spaces can be located by linux command line
            # gets the direction 
            if dataFile.find("R1") != -1:
                execRunFastqTotxt = 'python3 '+fastqTotxt+' '+configFile+' '+dataFile+' '+'F'
                print(execRunFastqTotxt)
                os.system(execRunFastqTotxt)
            else:
                continue
                execRunFastqTotxt = 'python3 '+fastqTotxt+' '+configFile+' '+dataFile+' '+'R'
                print(execRunFastqTotxt)
                os.system(execRunFastqTotxt)
            exit() 
    

    # Compiles design energy files from all design directories
    #compileDataFiles(energyFileName, dataDir, outFile)

    # Analyzes designs and outputs a submit file filled with sequences for backboneOptimization
    
    #execRunRepack = "condor_submit " + mslDir + "/" + ...
    #TODO: do I also add in a way to run the next step here? I'll need to assume that these files are all found in the same directory
    #os.system("condor_submit backboneOptimization.condor")
