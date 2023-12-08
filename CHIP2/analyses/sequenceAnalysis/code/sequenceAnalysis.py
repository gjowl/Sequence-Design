import os, sys, configparser
import pandas as pd

"""

"""
description = '''
This contains outputs for the sequenceAnalysis code. It takes the data from the reconstructed fluorescence of trimmed datasets
and analyzes the sequence composition against the fluorescence. Directories are named as follows:
    - clash: trim by the clashing mutant data
    - mutant_cutoff: fluorescence cutoff that the mutant must be less than to accept
    - percent_cutoff: another cutoff for mutants where the mutant fluorescence must be at least this much less than the WT to be accepted
    - number_of_mutants: the number of mutants necessary to be accepted for the WT design to be accepted
'''
# Helper file for reading the config file of interest for running the program
def read_config(configFile):
    config = configparser.ConfigParser()
    config.read(configFile)
    return config

def writeReadMe(config, outputDir):
    # loop through all of the config options
    with open(f'{outputDir}/README.txt', 'w') as f:
        f.write(description)
        # write the config options to the README
        for section in config.sections():
            f.write(f'\n\n{section}\n')
            for option in config[section]:
                f.write(f'{option} = {config[section][option]}\n')
        # close the file
        f.close()

# get filename separate from type and directory
def getFilename(file):
    programPath = os.path.realpath(file)
    programDir, programFile = os.path.split(programPath)
    filename, programExt = os.path.splitext(programFile)
    return filename

# get the current directory
cwd = os.getcwd()

# gets the name of this file to access the config options
programName = getFilename(__file__)

# get the config file options
configFile = sys.argv[1]
globalConfig = read_config(configFile)
config = globalConfig[programName]

# read in the config arguments
codeDir = config['codeDir']
clashDir = config['clashDir']
outputDir = config['outputDir']
requirementsFile = config['requirementsFile']
sequenceFile = config['sequenceFile']
mutantFile = config['mutantFile']

# check if output directory exists
if os.path.exists(outputDir):
    print(f"Output directory already exists. Delete {outputDir} to rerun.")
    sys.exit()
else:
    os.makedirs(outputDir, exist_ok=True)

if __name__ == "__main__":
    # write README file 
    writeReadMe(globalConfig, outputDir)

    # install the requirements
    execInstallRequirements = "pip install -r " + requirementsFile + " | { grep -v 'already satisfied' || :; }" 
    os.system(execInstallRequirements)

    # loop through the directories in the clash directory
    for input_dir in os.listdir(clashDir):
        # make sure the input directory is a directory
        if not os.path.isdir(f'{clashDir}/{input_dir}'):
            continue
        # get the input directory name
        outDir = outputDir + '/' + input_dir

        # run the script to add the necessary columns to the dataframes
        execAddColumns = f'python3 {codeDir}/addNecessaryColumns.py {clashDir}/{input_dir}/{sequenceFile} {clashDir}/{input_dir}/{mutantFile} {outDir}'
        os.system(execAddColumns)

        # run the voiding script if the voiding data is found in the config file
        #execplotBoxplot = f'python3 {codeDir}/plotBoxplotsPerAAPosition.py {outDir}/wt.csv {outDir}/mutant.csv {outDir}'
        #os.system(execplotBoxplot)

        # run boxplot script for all of the data
        execplotBoxplotCombined = f'python3 {codeDir}/plotBoxplotsCombined.py {outDir}/all.csv {outDir}'
        os.system(execplotBoxplotCombined)

        #execGraphDeltaFluorescence = f'python3 {codeDir}/graphDeltaFluorescence.py {outDir}/deltaFluorescence.csv {outDir}/deltaFluorescence'
        #os.system(execGraphDeltaFluorescence)