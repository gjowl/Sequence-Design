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
#rawDataDir = config['rawDataDir']
outputDir = config['outputDir']
requirementsFile = config['requirementsFile']
voidScript = config['voidScript']
# check if any of the clashing config options are found in the config file
voidData = 'voidScript' in config
if voidData:
    voidInputDir = config['voidInputDir']
    # below are hardcoded output names from the fluorescenceAnalysis code that as of 2023-9-11 gets used for voiding
    sequenceFile = f'{voidInputDir}/sequence_fluor_energy_data.csv'
    mutantFile = f'{voidInputDir}/mutant_fluor_energy_data.csv'

# make the output directory if it doesn't exist
if not os.path.exists(outputDir):
    os.makedirs(outputDir)

if __name__ == "__main__":
    # install the requirements
    execInstallRequirements = "pip install -r " + requirementsFile + " | { grep -v 'already satisfied' || :; }" 
    os.system(execInstallRequirements)

    # run the voiding script if the voiding data is found in the config file
    execVoidScript = f'python3 {codeDir}/checkVoidMutants.py {sequenceFile} {mutantFile} {outputDir}'
    os.system(execVoidScript)

    # run the plotting script
    execPlotScript = f'python3 {codeDir}/plotBoxplots.py {outputDir}/mutant_design_fluor.csv {outputDir}'
    os.system(execPlotScript)