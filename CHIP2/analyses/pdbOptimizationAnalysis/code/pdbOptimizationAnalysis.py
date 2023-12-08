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
rawDataDir = config['rawDataDir']
outputDir = config['outputDir']
kdeFile = config['kdeFile']
dataFile = config['dataFile']
requirementsFile = config['requirementsFile']
toxgreenFile = config['toxgreenFile']
strippedSequenceFile = config['strippedSequenceFile']
clashScript = config['clashScript']
# check if any of the clashing config options are found in the config file
clashData = 'clashScript' in config
if clashData:
    clashInputDir = config['clashInputDir']
    clashScript = config['clashScript']
    # separate the cutoffs by commas
    mutant_cutoffs = [float(x) for x in config['mutant_cutoff'].split(',')]
    percent_cutoffs = [float(x) for x in config['percent_cutoff'].split(',')]
    number_of_mutants_cutoffs = [int(x) for x in config['number_of_mutants_cutoff'].split(',')]
    # below are hardcoded output names from the fluorescenceAnalysis code that as of 2023-9-11 gets used for clashing
    sequenceFile = f'{clashInputDir}/sequence_fluor_energy_data.csv'
    mutantFile = f'{clashInputDir}/mutant_fluor_energy_data.csv'

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

    # strip the sequence ends (the first and last 3 amino acids) from the sequence file since some of the sequences have alanine vs leucine ends
    execStripSequenceEnds = f'python3 {codeDir}/stripSequenceEnds.py {toxgreenFile} {strippedSequenceFile} {outputDir}'
    os.system(execStripSequenceEnds)

    # compile the energy files
    execCompileEnergyFiles = f'python3 {codeDir}/compileFilesFromDirectories.py {rawDataDir} {dataFile} {outputDir}'
    os.system(execCompileEnergyFiles) 

    # add the percent gpa to the dataframe
    # get the dataFile name without the extension
    dataFilename = os.path.splitext(dataFile)[0]
    outputFile = f'{dataFilename}_percentGpa'
    execAddPercentGpA = f'python3 {codeDir}/addPercentGpaToDf.py {outputDir}/{dataFile}.csv {outputDir}/{strippedSequenceFile}.csv {outputFile} {outputDir}' 
    os.system(execAddPercentGpA)

    # check if you want to analyze clash data
    if clashData:
        for number_of_mutants_cutoff in number_of_mutants_cutoffs:
            for mutant_cutoff in mutant_cutoffs:
                for percent_cutoff in percent_cutoffs:
                    # convert the cutoffs to integers
                    mut, perc, num = int(mutant_cutoff*100), int(percent_cutoff*100), int(number_of_mutants_cutoff)
                    clashOutputDir = f'{outputDir}/clash_{mut}_{perc}_{num}'
                    execclashCheck = f'python3 {clashScript} {sequenceFile} {mutantFile} {clashOutputDir} {mutant_cutoff} {percent_cutoff} {number_of_mutants_cutoff}'
                    os.system(execclashCheck)
                    # loop through the files in the clashOutputDir
                    for filename in os.listdir(clashOutputDir):
                        # check if the file is a csv
                        if not filename.endswith('.csv'):
                            continue
                        file_outputDir = f'{clashOutputDir}/{os.path.splitext(filename)[0]}'
                        execAnalyzeclash = f'python3 {codeDir}/combineFilesAndPlot.py {clashOutputDir}/{filename} {outputDir}/{outputFile}.csv {file_outputDir} {codeDir}'
                        os.system(execAnalyzeclash)
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

    