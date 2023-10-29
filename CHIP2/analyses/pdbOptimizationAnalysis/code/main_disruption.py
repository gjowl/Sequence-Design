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
disruptionScript = config['disruptionScript']
# check if any of the disruptioning config options are found in the config file
disruptionData = 'disruptionScript' in config
if disruptionData:
    disruptionInputDir = config['disruptionInputDir']
    disruptionScript = config['disruptionScript']
    disruptionOutputDir = f'{outputDir}/{config["disruptionOutputDir"]}'
    wt_cutoff = config['wt_cutoff']
    mutant_cutoff = config['mutant_cutoff']
    percent_cutoff = config['percent_wt_cutoff'] # as of 2023-9-11 unused; but expect to use in the future
    number_of_mutants_cutoff = config['number_of_mutants_cutoff']
    # below are hardcoded output names from the fluorescenceAnalysis code that as of 2023-9-11 gets used for disruptioning
    sequenceFile = f'{disruptionInputDir}/sequence_fluor_energy_data.csv'
    mutantFile = f'{disruptionInputDir}/mutant_fluor_energy_data.csv'

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

    # check if you want to analyze disruption data
    if disruptionData:
        execDisruptionCheck = f'python3 {disruptionScript} {sequenceFile} {mutantFile} {disruptionOutputDir} {wt_cutoff} {mutant_cutoff} {percent_cutoff} {number_of_mutants_cutoff}'
        os.system(execDisruptionCheck)
        # loop through the files in the disruptionOutputDir
        for filename in os.listdir(disruptionOutputDir):
            # check if the file is a csv
            if not filename.endswith('.csv'):
                continue
            file_outputDir = f'{disruptionOutputDir}/{os.path.splitext(filename)[0]}'
            execAnalyzeDisruption = f'python3 {codeDir}/combineFilesAndPlot.py {disruptionOutputDir}/{filename} {outputDir}/{outputFile}.csv {file_outputDir}'
            os.system(execAnalyzeDisruption)

    # analyze the data
    execAnalyzeData = f'python3 {codeDir}/analyzeData.py {outputDir}/{outputFile}.csv {outputDir}' 
    os.system(execAnalyzeData)

    # convert to delta G
    execConvertToDeltaG = f'python3 {codeDir}/convertToDeltaG.py {outputDir}/{dataFile}.csv {outputDir}'
    os.system(execConvertToDeltaG)

    # graph the delta G
    execGraphDeltaG = f'python3 {codeDir}/graphDeltaG.py {outputDir}/{dataFile}_deltaG.csv {outputDir}'
    os.system(execGraphDeltaG)