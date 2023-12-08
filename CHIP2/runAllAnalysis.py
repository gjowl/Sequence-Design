'''
File: /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2/runAllAnalysis.py
Project: /home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2
Created Date: Friday December 8th 2023
Author: loiseau
-----
Description:
This script runs all of the analyses for the CHIP2 project. The analyses as of 12/8/2023 are:
    - toxgreenConversion.py
    - pdbOptimizationAnalysis.py
    - sequenceAnalysis.py
-----
'''

import os, sys, configparser

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

# gets the name of this file to access the config options
programName = getFilename(__file__)

# get the config file options
configFile = sys.argv[1]
globalConfig = read_config(configFile)
config = globalConfig[programName]

toxgreenConversionScript = config['toxgreenConversion']
pdbOptimizationAnalysisScript = config['pdbOptimizationAnalysis']
sequenceAnalysisScript = config['sequenceAnalysis']

# define the main directory
mainDir = '/home/loiseau@ad.wisc.edu/github/Sequence-Design/CHIP2'
analysisDir = f'{mainDir}/analyses'

# run the toxgreen conversion script
toxgreenConversion = f'python3 {mainDir}/toxgreenConversion/code/{toxgreenConversionScript} {configFile}'
os.system(toxgreenConversion)

# run the pdb optimization analysis script
pdbOptimizationAnalysis = f'python3 {analysisDir}/pdbOptimizationAnalysis/code/{pdbOptimizationAnalysisScript} {configFile}'
os.system(pdbOptimizationAnalysis)

# run the sequence analysis script
sequenceAnalysis = f'python3 {analysisDir}/sequenceAnalysis/code/{sequenceAnalysisScript} {configFile}'
os.system(sequenceAnalysis)
