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

outputDir = config['outputDir']
analysisCodeDir = config['analysisCodeDir']
toxgreenConversionScript = config['toxgreenConversion'] 
pdbOptimizationAnalysisScript = config['pdbOptimizationAnalysis']
sequenceAnalysisScript = config['sequenceAnalysis']
structureAnalysisScript = config['structureAnalysis']
hbondAnalysisScript = config['hbondAnalysis']
helperScript = config['helperScript'] # helper functions

# get the boolean for whether or not to run the analysis
runToxgreenConversion = config['runToxgreenConversion'].lower() == 'true'
runPdbOptimizationAnalysis = config['runPdbOptimizationAnalysis'].lower() == 'true'
runSequenceAnalysis = config['runSequenceAnalysis'].lower() == 'true'
runStructureAnalysis = config['runStructureAnalysis'].lower() == 'true'
runHbondAnalysis = config['runHbondAnalysis'].lower() == 'true'

# check if the name of the analysis directory is a directory (if it is, use it as the current working directory for the analysis code)
if os.path.isdir(analysisCodeDir):
    cwd = analysisCodeDir
else:
    # get the current working directory
    cwd = os.getcwd()
    # combine the two to get the analysis directory path
    cwd = f'{cwd}/{analysisCodeDir}'

'''
    Run the scripts of interest for analysis. If you want to add more analysis, you can add them to the below, but I'd suggest just making new scripts
    instead and just using some of the output data from this one. 
    
    The order below is the order that the analyses will be run in. It's kind of set in stone for some parts (ie. toxgreenConversion is needed for the
    pdbOptimizationAnalysis, which is needed to run sequenceAnalysis and structureAnalysis and hbondAnalysis)
'''

# make the output directory if it doesn't exist
os.makedirs(outputDir, exist_ok=True)
# copy the helper script to the output directory
os.system(f'cp {helperScript} {outputDir}')

# run the toxgreen conversion script
if runToxgreenConversion:
    toxgreenConversion = f'python3 {cwd}/toxgreenConversion/code/{toxgreenConversionScript} -config {configFile} -outputDir {outputDir}/toxgreenConversion -helperScript {helperScript}'
    #os.system(toxgreenConversion)
    #os.system(f'tar -czvf {outputDir}/toxgreenConversionCode.tar.gz {cwd}/toxgreenConversion/code')

# run the pdb optimization analysis script
if runPdbOptimizationAnalysis:
    pdbOptimizationAnalysis = f'python3 {cwd}/pdbOptimizationAnalysis/code/{pdbOptimizationAnalysisScript} -config {configFile} -outputDir {outputDir}/pdbOptimizationAnalysis -helperScript {helperScript}'
    os.system(pdbOptimizationAnalysis)
    os.system(f'tar -czvf {outputDir}/pdbOptimizationAnalysisCode.tar.gz {cwd}/pdbOptimizationAnalysis/code')

# run the sequence analysis script
if runSequenceAnalysis:
    sequenceAnalysis = f'python3 {cwd}/sequenceAnalysis/code/{sequenceAnalysisScript} -config {configFile} -outputDir {outputDir}/sequenceAnalysis -helperScript {helperScript}'
    #os.system(sequenceAnalysis)
    #os.system(f'tar -czvf {outputDir}/sequenceAnalysisCode.tar.gz {cwd}/sequenceAnalysis/code')

# run the structure analysis script
if runStructureAnalysis:
    structureAnalysis = f'python3 {cwd}/structureAnalysis/code/{structureAnalysisScript} -config {configFile} -outputDir {outputDir}/structureAnalysis -helperScript {helperScript}'
    os.system(structureAnalysis)
    os.system(f'tar -czvf {outputDir}/structureAnalysisCode.tar.gz {cwd}/structureAnalysis/code')

# run the hbond analysis script
if runHbondAnalysis:
    hbondAnalysis = f'python3 {cwd}/hbondAnalysis/code/{hbondAnalysisScript} -config {configFile} -outputDir {outputDir}/hbondAnalysis -helperScript {helperScript}'
    os.system(hbondAnalysis)
    os.system(f'tar -czvf {outputDir}/hbondAnalysisCode.tar.gz {cwd}/hbondAnalysis/code')