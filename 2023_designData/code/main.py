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
kdeFile = config['kdeFile']
seqEntropyFile = config['seqEntropyFile']
sequenceProbabilitiesFile = config['sequenceProbabilitiesFile']
rawDataDir = config['rawDataDir']
requirementsFile = config['requirementsFile']
compileEnergyScript = config['compileEnergyScript']
designAnalysisScript = config['designAnalysisScript']
createPseScript = config['createPseScript']
outputDir = config['outputDir']
dataFile = config['dataFile']
numSeqs = config['numSeqs']
createBackboneRepackScript = config['createBackboneRepackScript']

# check if the output directory exists
os.makedirs(name=outputDir, exist_ok=True)

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
    execCompileEnergyFiles = f'python3 {compileEnergyScript} {rawDataDir} {outputDir} {dataFile}'
    os.system(execCompileEnergyFiles)

    # execute design analysis script
    execDesignAnalysis = f'python3 {designAnalysisScript} {kdeFile} {seqEntropyFile} {dataFile} {outputDir} {numSeqs}'
    os.system(execDesignAnalysis)

    regions = ['GAS', 'Right', 'Left']
    # execute create pymol session files script
    for region in regions:
        execCreatePymolSessionFiles = f'python3 {createPseScript} {rawDataDir} {outputDir}/{region}'
        os.system(execCreatePymolSessionFiles)

    # create the csv file for submitting for backbone repacks
    execMakeBackboneRepackFile = f'python3 {createBackboneRepackScript} -inFile {dataFile} -outDir {outputDir}'
    os.system(execMakeBackboneRepackFile)