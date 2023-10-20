import os, sys, configparser
import pandas as pd

"""
Code for compiling energyFile.csv files from an input directory and analyzing the data
"""
# Helper file for reading the config file of interest for running the program
def read_config(configFile):
    config = configparser.ConfigParser()
    config.read(configFile)
    return config

# get the current directory
cwd = os.getcwd()

# get the config file options
configFile = sys.argv[1]
globalConfig = read_config(configFile)
config = globalConfig['main']

# read in the config arguments
codeDir = config['codeDir']
rawDataDir = config['rawDataDir']
outputDir = config['outputDir']
dataFile = config['dataFile']
requirementsFile = config['requirementsFile']
toxgreenFile = config['toxgreenFile']
clashScript = config['clashScript']
# check if any of the clashing config options are found in the config file
clashData = 'clashScript' in config
if clashData:
    clashInputDir = config['clashInputDir']
    clashScript = config['clashScript']
    clashOutputDir = f'{outputDir}/{config["clashOutputDir"]}'
    wt_cutoff = config['wt_cutoff']
    mutant_cutoff = config['mutant_cutoff']
    percent_cutoff = config['percent_wt_cutoff'] # as of 2023-9-11 unused; but expect to use in the future
    # below are hardcoded output names from the fluorescenceAnalysis code that as of 2023-9-11 gets used for clashing
    sequenceFile = f'{clashInputDir}/sequence_fluor_energy_data.csv'
    mutantFile = f'{clashInputDir}/mutant_fluor_energy_data.csv'

# make the output directory if it doesn't exist
if not os.path.exists(outputDir):
    os.makedirs(outputDir)

if __name__ == "__main__":
    # install the requirements
    execInstallRequirements = "pip install -r " + requirementsFile + " | { grep -v 'already satisfied' || :; }" 
    os.system(execInstallRequirements)

    # compile the energy files
    execCompileEnergyFiles = f'python3 {codeDir}/compileFilesFromDirectories.py {rawDataDir} {dataFile} {outputDir}'
    os.system(execCompileEnergyFiles) 

    # add the percent gpa to the dataframe
    # get the dataFile name without the extension
    dataFilename = os.path.splitext(dataFile)[0]
    outputFile = f'{dataFilename}_percentGpa'
    execAddPercentGpA = f'python3 {codeDir}/addPercentGpaToDf.py {outputDir}/{dataFile}.csv {toxgreenFile} {outputFile} {outputDir}' 
    os.system(execAddPercentGpA)

    # check if you want to analyze clashing data
    if clashData:
        execClashCheck = f'python3 {clashScript} {sequenceFile} {mutantFile} {clashOutputDir} {wt_cutoff} {mutant_cutoff} {percent_cutoff}'
        os.system(execClashCheck)
        # loop through the files in the clashOutputDir
        for filename in os.listdir(clashOutputDir):
            # check if the file is a csv
            if not filename.endswith('.csv'):
                continue
            file_outputDir = f'{clashOutputDir}/{os.path.splitext(filename)[0]}'
            execAnalyzeClash = f'python3 {codeDir}/combineFilesAndPlot.py {clashOutputDir}/{filename} {outputDir}/{outputFile}.csv {file_outputDir}'
            os.system(execAnalyzeClash)

    # analyze the data
    execAnalyzeData = f'python3 {codeDir}/analyzeData.py {outputDir}/{outputFile}.csv {outputDir}' 
    os.system(execAnalyzeData)

    # convert to delta G
    execConvertToDeltaG = f'python3 {codeDir}/convertToDeltaG.py {outputDir}/{outputFile}.csv {outputDir}'
    os.system(execConvertToDeltaG)

    # graph the delta G
    execGraphDeltaG = f'python3 {codeDir}/graphDeltaG.py {outputDir}/{outputFile}_deltaG.csv {outputDir}'
    os.system(execGraphDeltaG)