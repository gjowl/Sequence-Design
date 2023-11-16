import os, sys, configparser
import pandas as pd

"""
Code for compiling energyFile.csv files from an input directory and analyzing the data
"""
description = '''
This contains outputs for the pdbOptimizationAnalysis code. It extracts the energetics from a C++ program that predicts
structures of mutant proteins based on a given dimeric pdb structure. The analysis for those energies, according to the 
below given options, is found within this directory. Directories named as follows:
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
kdeFile = config['kdeFile']
dataFile = config['dataFile']
requirementsFile = config['requirementsFile']
toxgreenFile = config['toxgreenFile']
disruptionScript = config['disruptionScript']
# check if any of the disruptioning config options are found in the config file
disruptionData = 'disruptionScript' in config
if disruptionData:
    disruptionInputDir = config['disruptionInputDir']
    disruptionScript = config['disruptionScript']
    # separate the cutoffs by commas
    mutant_cutoffs = [float(x) for x in config['mutant_cutoff'].split(',')]
    percent_cutoffs = [float(x) for x in config['percent_cutoff'].split(',')]
    number_of_mutants_cutoff = config['number_of_mutants_cutoff']
    # below are hardcoded output names from the fluorescenceAnalysis code that as of 2023-9-11 gets used for disruptioning
    sequenceFile = f'{disruptionInputDir}/sequence_fluor_energy_data.csv'
    mutantFile = f'{disruptionInputDir}/mutant_fluor_energy_data.csv'

# make the output directory if it doesn't exist
if not os.path.exists(outputDir):
    os.makedirs(outputDir)

if __name__ == "__main__":
    # write README file 
    writeReadMe(globalConfig, outputDir)
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
        for mutant_cutoff, percent_cutoff in zip(mutant_cutoffs, percent_cutoffs):
            # convert the cutoffs to integers
            mut, perc, num = int(mutant_cutoff*100), int(percent_cutoff*100), int(number_of_mutants_cutoff)
            disruptionOutputDir = f'{outputDir}/clash_{mut}_{perc}_{num}'
            execDisruptionCheck = f'python3 {disruptionScript} {sequenceFile} {mutantFile} {disruptionOutputDir} {mutant_cutoff} {percent_cutoff} {number_of_mutants_cutoff}'
            os.system(execDisruptionCheck)
            # loop through the files in the disruptionOutputDir
            for filename in os.listdir(disruptionOutputDir):
                # check if the file is a csv
                if not filename.endswith('.csv'):
                    continue
                file_outputDir = f'{disruptionOutputDir}/{os.path.splitext(filename)[0]}'
                execAnalyzeDisruption = f'python3 {codeDir}/combineFilesAndPlot.py {disruptionOutputDir}/{filename} {outputDir}/{outputFile}.csv {file_outputDir}'
                os.system(execAnalyzeDisruption)
                file_to_analyze = 'lowestEnergySequences'
                # plot kde plots of geometries
                execPlotKde = f'python3 {codeDir}/makeKdePlots.py {kdeFile} {file_outputDir}/{file_to_analyze}.csv {file_outputDir}'
                os.system(execPlotKde)
            # convert to delta G
            execConvertToDeltaG = f'python3 {codeDir}/convertToDeltaG.py {file_outputDir}/{file_to_analyze}.csv {file_outputDir}'
            os.system(execConvertToDeltaG)

            # graph the delta G
            execGraphDeltaG = f'python3 {codeDir}/graphDeltaG.py {file_outputDir}/{file_to_analyze}_deltaG.csv {file_outputDir}'
            os.system(execGraphDeltaG)

    # analyze the data
    execAnalyzeData = f'python3 {codeDir}/analyzeData.py {outputDir}/{outputFile}.csv {outputDir}' 
    os.system(execAnalyzeData)

    