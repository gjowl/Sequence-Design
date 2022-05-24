# @Author: Gilbert Loiseau
# @Date:   2021-12-25
# @Filename: runDesignAndMakeCHIP.py
# @Last modified by:   Gilbert Loiseau
# @Last modified time: 2022/03/21

"""
This file will run multiple python scripts for compiling ngs data and reconstructing the fluorescence profile.
"""

from fileinput import filename
import sys
import os
import pandas as pd
from functions import *

# Use the utilityFunction to get the configFile
configFile = getConfigFile(sys.argv[1])
# gets the name of this file to access 
programName = getFilename(__file__)

# Read in configuration file:
globalConfig = read_config(configFile)
config = globalConfig[programName]

# Config file options:
outputDir            = config["outputDir"]
requirementsFile     = config["requirementsFile"]
dataDir              = config["dataDir"]
fastqTotxt           = config["fastqTotxt"]
ngsAnalysis          = config["ngsAnalysis"]
countFile            = config["countFile"]
percentFile          = config["percentFile"]
refFile              = config["refFile"]
namesFile              = config["namesFile"]

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

    # runs through all files in the dataDir and converts fastq to txt; only runs if no files are found in the output dir
    convertFastqToTxt(fastqTotxt, namesFile, refFile, dataDir, outputDir)
    # get list of sequences
    seqIdDf = outputGoodSequenceDataframe(outputDir)
    # get the sequence column (first column) and skip the summary data rows
    seqColumn = seqIdDf.iloc[:,0].tolist()

    # make csv with sequence counts for all files
    # go through all files and save counts in dictionary
    outputSequenceCountsCsv(seqColumn, outputDir, countFile)
    outputSequencePercentsCsv(seqColumn, outputDir, percentFile)
    seqIdDf = seqIdDf.drop_duplicates(subset='Sequence', keep='first')
    seqIdDf = seqIdDf.reset_index(drop=True)
    appendColumnFromInputFile(seqIdDf, 'Segment', countFile)
    appendColumnFromInputFile(seqIdDf, 'Segment', percentFile)

    # execute ngsAnalysis script 
    execNgsAnalysis = 'python3 '+ngsAnalysis+' '+configFile
    print(execNgsAnalysis)
    os.system(execNgsAnalysis)