'''
File: d:\github\Sequence-Design\ngsReconstruction\CHIP2_analysisCode\main.py
Project: d:\github\Sequence-Design\ngsReconstruction\CHIP2_analysisCode
Created Date: Saturday August 19th 2023
Author: gjowl
-----
Last Modified: Saturday August 19th 2023 7:22:53 pm
Modified By: gjowl
-----
Description:  
A driver script for converting reconstructed fluorescence data to toxgreen fluorescence data.
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------
'''

import sys, os, pandas as pd, numpy as np, matplotlib.pyplot as plt
import configparser
from configparser import ConfigParser

# Method to read config file settings
# Helper file for reading the config file of interest for running the program
def read_config(configFile):
    config = configparser.ConfigParser()
    config.read(configFile)
    return config

# get filename separate from type and directory
def getFilename(file):
    programPath = os.path.realpath(file)
    programDir, programFile = os.path.split(programPath)
    filename, programExt = os.path.splitext(programFile)
    return filename

# the input global (multi-part) configuration file
configFile = sys.argv[1]

# gets the name of this file to access the config options from it's section of the config file
programName = getFilename(__file__) # toxgreenConversion

# Read in configuration file options
globalConfig = read_config(configFile)
config = globalConfig[programName]

# Config file options
outputDir               = config["outputDir"]
inputDir                = config["inputDir"]

'''
    setting up the directory to be able to rerun the program
'''
# copy the original config file to the output directory
os.system(f'cp {configFile} {outputDir}/originalConfig.config')

# check if the input files directory exists
newInputDir = f'{outputDir}/inputFiles'
os.makedirs(newInputDir, exist_ok=True)

# check if the new input directory is empty (if it is, copy the input files to the new input directory)
if len(os.listdir(newInputDir)) == 0:
    os.system(f'cp {inputDir}/* {newInputDir}')
    # copy the reconstruction file to the output directory (from the ngsReconstruction data in ngsReconstruction/NAMEOFRECONSTRUCTION/reconstructedData/)
    os.system(f'cp {config["reconstructionFile"]} {newInputDir}')
# rename the input directory to the new input directory
inputDir = newInputDir

# get the script directory
scriptDir               = config["scriptDir"]

'''
    reading the config file options
'''
# input files
# get just the name of the reconstruction file with the extension
reconstructionFilename = getFilename(config["reconstructionFile"]) + '.csv'
requirementsFile        = f'{inputDir}/{config["requirementsFile"]}'
wtSequenceFile          = f'{inputDir}/{config["wtSequenceComputationFile"]}'
mutantSequenceFile      = f'{inputDir}/{config["mutantSequenceComputationFile"]}'
controlFlowFile         = f'{inputDir}/{config["controlFlowFile"]}'
reconstructionFile      = f'{inputDir}/{reconstructionFilename}'

# scripts to run
adjustFluorByControlFlow = f'{scriptDir}/{config["adjustFluorScript"]}'
filteringScript          = f'{scriptDir}/{config["filteringScript"]}'
sequenceVsMutantScript   = f'{scriptDir}/{config["sequenceVsMutantScript"]}'
graphScript              = f'{scriptDir}/{config["graphScript"]}'
graphScript2             = f'{scriptDir}/{config["graphScript2"]}'
seqDir                   = f'{outputDir}/{config["seqDir"]}'
filteringDir             = f'{outputDir}/{config["filteringDir"]}'
graphingDir              = f'{outputDir}/{config["graphingDir"]}'

# booleans if you only want to rerun partial
runAdjustFluor           = config["runAdjustFluor"].lower() == 'true'
runfilterWithComputation = config["runFilterWithComputation"].lower() == 'true'
runfilterBeforeGraphing  = config["runFilterBeforeGraphing"].lower() == 'true'
runSequenceVsMutant      = config["runSequenceVsMutant"].lower() == 'true'
runGraphing              = config["runGraphing"].lower() == 'true'

# check if output directory exists
os.makedirs(outputDir, exist_ok=True)
# copy the config file to the output directory (setting up the rerun.config file for the next run)
# if this works well, you should just be able to run: python3 PATHTOCODE/PROGRAMNAME rerun.config
configParser  = ConfigParser()
configParser.read(configFile)
configParser.set('toxgreenConversion', 'outputDir', outputDir)
configParser.set('toxgreenConversion', 'inputDir', inputDir)
configParser.set('toxgreenConversion', 'reconstructionFile', reconstructionFilename)
with open(f'{outputDir}/rerun.config', 'w') as configfile:
    configParser.write(configfile)

if __name__ == '__main__':
    print('Running toxgreenConversion.py...')
    #install required packages for the below programs; these are found in requirements.txt
    #if you decide to add more packages to these programs, execute the below and it will update the requirements file:
    #   -pip freeze > requirements.txt
    #tips for requirements files:
    #  https://pip.pypa.io/en/latest/reference/requirements-file-format/#requirements-file-format
    #  gets rid of requirement output: https://github.com/pypa/pip/issues/5900?msclkid=474dd7c0c72911ec8bf671f1ae3975f0
    #execInstallRequirements = "pip install -r " + requirementsFile
    ##execInstallRequirements = "pip install -r " + requirementsFile + " | { grep -v 'already satisfied' || :; }" 
    #os.system(execInstallRequirements)

    # adjust fluorescence by control flow
    if runAdjustFluor:
        execAdjustFluor = f'python3 {adjustFluorByControlFlow} -recFile {reconstructionFile} -flowFile {controlFlowFile} -outDir {outputDir}'
        print(f' - Running: {execAdjustFluor}')
        os.system(execAdjustFluor)

    # filter with computation (this barely does anything other than outputting files with their attached initial design data)
    if runfilterWithComputation:
        fluorFile = f'{outputDir}/all_transformed.csv'
        execMutantAnalysis = f'python3 {filteringScript} -fluorFile {fluorFile} -seqFile {wtSequenceFile} -mutFile {mutantSequenceFile} -outDir {filteringDir}'
        print(f' - Running: {execMutantAnalysis}')
        os.system(execMutantAnalysis)

    # sequence vs mutant analysis
    # graphing code (this was kind of my initial analysis. I likely will not use any of this in the paper, but it's here for reference if I need it as of 2024-2-24)
    #if runSequenceVsMutant:
    #    fluorFile = f'{filteringDir}/all.csv'
    #    execSequenceVsMutant = f'python3 {sequenceVsMutantScript} -fluorFile {fluorFile} -outDir {seqDir}'
    #    print(f' - Running: {execSequenceVsMutant}')
    #    os.system(execSequenceVsMutant)

    # loop through the files in the final output directory and graph them
    #if runGraphing:
    #    file_list = os.listdir(seqDir)
    #    for file in file_list:
    #        if file.endswith('.csv'):
    #            # get filename separate from type and directory
    #            programPath = os.path.realpath(file)
    #            programDir, programFile = os.path.split(programPath)
    #            file_name, programExt = os.path.splitext(programFile)
    #            inputFile = f'{seqDir}/{file}'
    #            fluorDir = f'{seqDir}/{file_name}'
    #            outDir = f'{graphingDir}/{file_name}'
    #            fluorFile = f'{fluorDir}/sequence_fluor_energy_data.csv'
    #            execGraphing = f'python3 {graphScript} -inFile {fluorFile} -outDir {outDir}'
    #            os.system(execGraphing)
    #            individualOutDir = f'{outDir}/individual_graphs'
    #            execIndividualGraphing = f'python3 {graphScript2} -inFile {fluorFile} -outDir {individualOutDir}'
    #            os.system(execIndividualGraphing)