import sys, os
import configparser

# Helper file for reading the config file of interest for running the program
def read_config(configFile):
    config = configparser.ConfigParser()
    config.read(configFile)
    return config

# read in the config file
configFile = sys.argv[1]
globalConfig = read_config(configFile)
config = globalConfig['main']

# read in the config arguments
untarScript = config['untarFolders']
addPdbsScript = config['addPdbsToDir']
createCsvScript = config['createCalcEnergyCsv']
inputDir = config['inputDir']
outputFile = config['outputFile']
extractionDir = config['extractionDir']
pdbDir = config['pdbDir']

# create the output directories
os.makedirs(name=extractionDir, exist_ok=True)
os.makedirs(name=pdbDir, exist_ok=True)

if __name__ == '__main__':
    # untar the files
    #execUntar = f'python3 {untarScript} {inputDir} {extractionDir}'
    #os.system(execUntar)

    # TODO: add in code to edit pdb files to remove mem and other unnecessary info

    # add the pdb files to the output directory
    execAddPdbs = f'python3 {addPdbsScript} {extractionDir} {pdbDir}'
    os.system(execAddPdbs)

    # create the csv file
    execCreateCsv = f'python3 {createCsvScript} {extractionDir} {outputFile}'
    os.system(execCreateCsv)
