import sys
import os
import pandas as pd
from functions import *

'''
This file is the main program for running analysis on design data. It reads in a config file and runs the analysis
through other files in the code directory
'''

# read in the config file
configFile = sys.argv[1]
globalConfig = read_config(configFile)
config = globalConfig['main']

# read in the config arguments
#kdeFile = config['kdeFile']
#seqEntropyFile = config['seqEntropyFile']
#sequenceProbabilitiesFile = config['sequenceProbabilitiesFile']
#rawDataDir = config['rawDataDir']
requirementsFile = config['requirementsFile']
compileEnergyScript = config['compileEnergyScript']
designAnalysisScript = config['designAnalysisScript']
createPseScript = config['createPseScript']
outputDir = config['outputDir']

# check if the output directory exists
if not os.path.isdir(outputDir):
    os.mkdir(outputDir)

if __name__ == '__main__':
    #install required packages for the below programs; these are found in requirements.txt
    #if you decide to add more packages to these programs, execute the below and it will update the requirements file:
    #   -pip freeze > requirements.txt
    #tips for requirements files:
    #  https://pip.pypa.io/en/latest/reference/requirements-file-format/#requirements-file-format
    #  gets rid of requirement output: https://github.com/pypa/pip/issues/5900?msclkid=474dd7c0c72911ec8bf671f1ae3975f0
    execInstallRequirements = "pip install -r " + requirementsFile + " | { grep -v 'already satisfied' || :; }" 
    os.system(execInstallRequirements)
    
    # execute compile script 
    execCompileEnergyFiles = 'python3 '+compileEnergyScript+' '+configFile
    os.system(execCompileEnergyFiles)

    # execute design analysis script
    execDesignAnalysis = 'python3 '+designAnalysisScript+' '+configFile
    os.system(execDesignAnalysis)

    # execute create pymol session files script
    #execCreatePymolSessionFiles = 'python3 '+createPseScript+' '+configFile
    #os.system(execCreatePymolSessionFiles)