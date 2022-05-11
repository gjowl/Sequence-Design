# @Author: Gilbert Loiseau
# @Date:   2021-12-25
# @Filename: runDesignAndMakeCHIP.py
# @Last modified by:   Gilbert Loiseau
# @Last modified time: 2022/03/21

"""
This file will run multiple python scripts for compiling ngs data and then analyzing.
"""

from fileinput import filename
import sys
import os
import helper
import pandas as pd
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
testDir              = config["testDir"]
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

    # runs through all files in the dataDir and converts fastq to txt; only runs if no files are found in the output dir
    convertFastqToTxt(fastqTotxt, configFile, dataDir, outputDir)
    
    # get list of sequences
    listSeq = getSequenceList(outputDir)

    # make csv with sequence counts for all files
    # go through all files and save counts in dictionary
    outFile = testDir+"allCounts.csv"
    outputSequenceCountsCsv(listSeq, outputDir, outFile)

    #execRunRepack = "condor_submit " + mslDir + "/" + ...
    #TODO: do I also add in a way to run the next step here? I'll need to assume that these files are all found in the same directory
    #os.system("condor_submit backboneOptimization.condor")
