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
configFile = sys.argv[1]
# gets the name of this file to access 
programName = getFilename(__file__)

# Read in configuration file:
globalConfig = read_config(configFile)
config = globalConfig[programName]

# Config file options:
outputDir            = config["outputDir"]
extractionDir        = config["extractionDir"]
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
    os.makedirs(name=outputDir, exist_ok=True)
    os.makedirs(name=extractionDir, exist_ok=True)

    #install required packages for the below programs; these are found in requirements.txt
    #if you decide to add more packages to these programs, execute the below and it will update the requirements file:
    #   -pip freeze > requirements.txt
    #tips for requirements files:
    #  https://pip.pypa.io/en/latest/reference/requirements-file-format/#requirements-file-format
    #  gets rid of requirement output: https://github.com/pypa/pip/issues/5900?msclkid=474dd7c0c72911ec8bf671f1ae3975f0
    execInstallRequirements = "pip install -r " + requirementsFile + " | { grep -v 'already satisfied' || :; }" 
    #os.system(execInstallRequirements)

    # runs through all files in the dataDir and converts fastq to txt; only runs if no files are found in the output dir
    convertFastqToTxt(fastqTotxt, namesFile, refFile, dataDir, extractionDir)
    # TODO: edited the above to not remove sequences without fwd primer, but this messes up controls, in particular GpA and G83I. I think if I just add in 
    # a bit of other code for matching with these sequences from the sequencing txt files it should work
    
    # get list of sequences and add to dataframe
    seqIdDf = extractGoodSequenceDataframe(extractionDir, outputDir)
    # save the dataframe to a csv file
    seqIdDf.to_csv(outputDir+'seqIdDf.csv', index=False)

    ## get the sequence column (first column) and skip the summary data rows
    #seqColumn = seqIdDf.iloc[:,0].tolist()

    ## compile counts and percents from data files
    ## go through all files and save into csv file
    #outputSequenceCountsCsv(seqColumn, extractionDir, countFile)
    #outputSequencePercentsCsv(seqColumn, extractionDir, percentFile)

    ## drop duplicates and reset the index
    #seqIdDf = seqIdDf.drop_duplicates(subset='Sequence', keep='first')
    #seqIdDf = seqIdDf.reset_index(drop=True)

    ## add the segment number to the counts and percents files to separate sequences by segment number
    #appendColumnFromInputFile(seqIdDf, 'Segment', countFile)
    #appendColumnFromInputFile(seqIdDf, 'Segment', percentFile)

    # execute ngsAnalysis script 
    execNgsAnalysis = 'python3 '+ngsAnalysis+' '+configFile
    print(execNgsAnalysis)
    os.system(execNgsAnalysis)