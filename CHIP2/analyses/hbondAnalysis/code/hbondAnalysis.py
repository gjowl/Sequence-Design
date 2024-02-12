import os, sys, configparser
import pandas as pd
description = '''
This contains outputs for the hbondAnalysis code. It analyzes pdb structures to determine the number of 
hydrogen bonds that are possible based on a given distance cutoff, and it outputs analyzed data.
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
pseDir = config['pseDir']
hbondFile = config['hbondFile']
plotDataFile = config['plotDataFile']
dataFile = config['dataFile']
outputDir = config['outputDir']
requirementsFile = config['requirementsFile']
# make the output directory if it doesn't exist
os.makedirs(outputDir, exist_ok=True)
if __name__ == "__main__":
    # write README file 
    writeReadMe(globalConfig, outputDir)
    ## install the requirements
    #execInstallRequirements = "pip install -r " + requirementsFile + " | { grep -v 'already satisfied' || :; }" 
    #os.system(execInstallRequirements)

    # get the hbonddata
    #execGetHbondData = f'python3 {codeDir}/potentialHbondCounter.py -pseDir {pseDir} -outFile {hbondFile} -outDir {outputDir} -hbondDistance 3.3'
    #os.system(execGetHbondData)
    execGetHbondData = f'python3 {codeDir}/potentialHbondCounter.py -pseDir {pseDir} -outFile {hbondFile} -outDir {outputDir} -hbondDistance 3.3'
    os.system(execGetHbondData)

    ## merge the data
    #execMergeData = f'python3 {codeDir}/mergeDf.py -inFile {dataFile} -fileToMerge {outputDir}/{hbondFile}.csv -outFile {plotDataFile} -outDir {outputDir}'
    #os.system(execMergeData)
    # merge the data
    execMergeData = f'python3 {codeDir}/mergeDf.py -inFile {dataFile} -fileToMerge {outputDir}/{hbondFile}.csv -outFile {plotDataFile} -outDir {outputDir}'
    os.system(execMergeData)

    # makes plots of the data
    execMakePlots = f'python3 {codeDir}/plotHbondData.py -inFile {outputDir}/{plotDataFile}.csv -outDir {outputDir}'
    os.system(execMakePlots)