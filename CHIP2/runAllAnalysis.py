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

analysisCodeDir = config['analysisCodeDir'] # can input an entire directory or just the directory name from current working directory
toxgreenConversionScript = config['toxgreenConversion'] 
pdbOptimizationAnalysisScript = config['pdbOptimizationAnalysis']
sequenceAnalysisScript = config['sequenceAnalysis']
boxplotAnalysisScript = config['boxplotAnalysis']
hbondAnalysisScript = config['hbondAnalysis']

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
    pdbOptimizationAnalysis, which is needed to run sequenceAnalysis and boxplotAnalysis and hbondAnalysis)
'''
# run the toxgreen conversion script
toxgreenConversion = f'python3 {cwd}/toxgreenConversion/code/{toxgreenConversionScript} {configFile}'
os.system(f'tar -czvf toxgreenConversionCode.tar.gz {cwd}/toxgreenConversion/code')
os.system(toxgreenConversion)

# run the pdb optimization analysis script
pdbOptimizationAnalysis = f'python3 {cwd}/pdbOptimizationAnalysis/code/{pdbOptimizationAnalysisScript} {configFile}'
os.system(f'tar -czvf pdbOptimizationAnalysisCode.tar.gz {cwd}/pdbOptimizationAnalysis/code')
os.system(pdbOptimizationAnalysis)

# run the sequence analysis script
sequenceAnalysis = f'python3 {cwd}/sequenceAnalysis/code/{sequenceAnalysisScript} {configFile}'
os.system(f'tar -czvf sequenceAnalysisCode.tar.gz {cwd}/sequenceAnalysis/code')
os.system(sequenceAnalysis)

# run the boxplot analysis script
boxplotAnalysis = f'python3 {cwd}/boxplotAnalysis/code/{boxplotAnalysisScript} {configFile}'
os.system(f'tar -czvf boxplotAnalysisCode.tar.gz {cwd}/boxplotAnalysis/code')
os.system(boxplotAnalysis)

# run the hbond analysis script
hbondAnalysis = f'python3 {cwd}/hbondAnalysis/code/{hbondAnalysisScript} {configFile}'
os.system(f'tar -czvf hbondAnalysisCode.tar.gz {cwd}/hbondAnalysis/code')
os.system(hbondAnalysis)