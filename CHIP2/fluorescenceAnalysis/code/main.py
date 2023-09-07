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
A driver script for the CHIP2 analysis pipeline.
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------
'''

import sys, os, pandas as pd, numpy as np, matplotlib.pyplot as plt
import configparser

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

# read in the input configuration file
configFile = sys.argv[1]

# gets the name of this file to access 
programName = getFilename(__file__)

# Read in configuration file:
globalConfig = read_config(configFile)
config = globalConfig[programName]

# Config file options:
outputDir               = config["outputDir"]
# input files
inputDir                = config["inputDir"]
requirementsFile        = f'{inputDir}/{config["requirementsFile"]}'
reconstructionFile      = f'{inputDir}/{config["reconstructionFile"]}'
wtSequenceFile          = f'{inputDir}/{config["wtSequenceComputationFile"]}'
mutantSequenceFile      = f'{inputDir}/{config["mutantSequenceComputationFile"]}'
controlFlowFile         = f'{inputDir}/{config["controlFlowFile"]}'
# scripts to run
scriptDir               = config["scriptDir"]
adjustFluorByControlFlow = f'{scriptDir}/{config["adjustFluorScript"]}'
filteringScript         = f'{scriptDir}/{config["filteringScript"]}'
sequenceVsMutantScript  = f'{scriptDir}/{config["sequenceVsMutantScript"]}'
graphScript             = f'{scriptDir}/{config["graphScript"]}'
graphScript2            = f'{scriptDir}/{config["graphScript2"]}'
seqDir                  = f'{outputDir}/{config["seqDir"]}'
filteringDir            = f'{outputDir}/{config["filteringDir"]}'
graphingDir            = f'{outputDir}/{config["graphingDir"]}'

# booleans if you only want to rerun partial
runAdjustFluor           = config["runAdjustFluor"].lower() == 'true'
runfilterWithComputation = config["runFilterWithComputation"].lower() == 'true'
runfilterBeforeGraphing  = config["runFilterBeforeGraphing"].lower() == 'true'
runSequenceVsMutant      = config["runSequenceVsMutant"].lower() == 'true'
runGraphing              = config["runGraphing"].lower() == 'true'

if __name__ == '__main__':
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
        execAdjustFluor = f'python3 {adjustFluorByControlFlow} {reconstructionFile} {controlFlowFile} {outputDir}'
        os.system(execAdjustFluor)

    # mutant analysis
    if runfilterWithComputation:
        fluorFile = f'{outputDir}/all_transformed.csv'
        execMutantAnalysis = f'python3 {filteringScript} {fluorFile} {wtSequenceFile} {mutantSequenceFile} {filteringDir}'
        os.system(execMutantAnalysis)

    # sequence vs mutant
    if runSequenceVsMutant:
        fluorFile = f'{filteringDir}/all.csv'
        execSequenceVsMutant = f'python3 {sequenceVsMutantScript} {fluorFile} {seqDir}'
        os.system(execSequenceVsMutant)

    # graphing code
    # TODO: probably loop this through whatever outputs you want to graph from the previous two scripts 
    # loop through the files in the final output directory and graph them
    if runGraphing:
        file_list = os.listdir(seqDir)
        for file in file_list:
            if file.endswith('.csv'):
                # get filename separate from type and directory
                programPath = os.path.realpath(file)
                programDir, programFile = os.path.split(programPath)
                file_name, programExt = os.path.splitext(programFile)
                inputFile = f'{seqDir}/{file}'
                fluorDir = f'{seqDir}/{file_name}'
                if runfilterBeforeGraphing:
                    execMutantAnalysis = f'python3 {filteringScript} {inputFile} {wtSequenceFile} {mutantSequenceFile} {fluorDir}'
                    os.system(execMutantAnalysis)
                outDir = f'{graphingDir}/{file_name}'
                fluorFile = f'{fluorDir}/sequence_fluor_energy_data.csv'
                execGraphing = f'python3 {graphScript} {fluorFile} {outDir}'
                os.system(execGraphing)
                individualOutDir = f'{outDir}/individual_graphs'
                execIndividualGraphing = f'python3 {graphScript2} {fluorFile} {individualOutDir}'
                os.system(execIndividualGraphing)
    
    # will now output graphs for anything that gets output from the sequenceVsMutant script
    # continue to use that to trim data and see if I can split some clash/void data there
    # TODO: anyway to rationalize voids and clashes with reasonable and unreasonable data? Maybe
    #       just try a bunch of different cutoffs and see what works best?