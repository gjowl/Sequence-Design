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

# scripts to run
scriptDir               = config["scriptDir"]
graphScript             = f'{scriptDir}/{config["graphScript"]}'
graphScript2            = f'{scriptDir}/{config["graphScript2"]}'
seqDir                  = f'{outputDir}/{config["seqDir"]}'
graphingDir            = f'{outputDir}/{config["graphingDir"]}'

if __name__ == '__main__':
    # loop through the files in the final output directory and graph them
    file_list = os.listdir(seqDir)
    for file in file_list:
        if file.endswith('.csv'):
            # get filename separate from type and directory
            programPath = os.path.realpath(file)
            programDir, programFile = os.path.split(programPath)
            file_name, programExt = os.path.splitext(programFile)
            fluorDir = f'{seqDir}/{file_name}'
            outDir = f'{graphingDir}/{file_name}'
            seqFile = f'{fluorDir}/sequence_fluor_energy_data.csv'
            mutantFile = f'{fluorDir}/mutant_fluor_energy_data.csv'
            execGraphing = f'python3 {graphScript} {fluorFile} {mutantFile} {energyFile} {outDir}'
            os.system(execGraphing)
            individualOutDir = f'{outDir}/individual_graphs'
            execIndividualGraphing = f'python3 {graphScript2} {fluorFile} {mutantFile} {energyFile} {individualOutDir}'
            os.system(execIndividualGraphing)