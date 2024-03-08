'''
File: d:\github\Sequence-Design\CHIP2\analyses\figureMaking\code\main.py
Project: d:\github\Sequence-Design\CHIP2\analyses\figureMaking\code
Created Date: Saturday October 7th 2023
Author: gjowl
-----
Last Modified: Saturday October 7th 2023 12:42:41 pm
Modified By: gjowl
-----
Description:

-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------
'''

import os, sys, configparser, argparse

'''
    parse the command line arguments
'''
# initialize the parser
parser = argparse.ArgumentParser(description='Adjust the reconstructed fluorescence by the flow fluorescence of the controls')

# add the necessary arguments
parser.add_argument('-config','--config', type=str, help='the input configuration file')
parser.add_argument('-outputDir','--outputDir', type=str, help='the output directory')
parser.add_argument('-helperScript','--helperScript', type=str, help='the helper script file')

# extract the arguments into variables
args = parser.parse_args()
configFile = args.config
helperScript = args.helperScript
# import the functions from the helper code and get the program name
exec(open(helperScript).read())
programName = getFilename(__file__) # toxgreenConversion

# default value for the output directory (if not given, the current working directory is used + the program name)
outputDir = f'{os.getcwd()}/{programName}'
if args.outputDir is not None:
    outputDir = args.outputDir
    os.makedirs(outputDir, exist_ok=True)

'''
    read in the config file options and set up the directory to be able to rerun the program
'''
# get the config file options
globalConfig = read_config(configFile)
config = globalConfig[programName]

# Config file options
inputDir   = config["inputDir"]

'''
    copy the input files into the output directory
'''
# copy the original config file to the output directory
os.system(f'cp {configFile} {outputDir}/originalConfig.config')

# copy the input files directory to the output directory
inputDir, config = copyInputFiles(inputDir, outputDir, config) # inputDir is now the new input directory within the output directory, and config has been updated with the new file paths

'''
    reading the config file options
'''
# read in the input files
dataFile         = f'{inputDir}/{config["dataFile"]}' # file with the raw data information, including the directory of the pdb files for each sequence
sequenceFile     = f'{inputDir}/{config["sequenceFile"]}' # file with the sequences of interest
interfaceFile    = f'{inputDir}/{config["interfaceFile"]}' # file with the correct interfaces for each sequence
requirementsFile = f'{inputDir}/{config["requirementsFile"]}'

# read in the other arguments
scriptDir = config['scriptDir']
rawDataDirAla = config['rawDataDirAla'] # where the pdbs for the sequences are located
rawDataDirLeu = config['rawDataDirLeu'] # where the pdbs for the sequences are located
optimizedPdbDir = config['optimizedPdbDir'] # where the pdbs for the sequences are located
percentGpACutoff = float(config['percentGpACutoff'])

# copy the config file to the output directory (setting up the rerun.config file for the next run)
# if this works well, you should just be able to run: python3 PATHTOCODE/PROGRAMNAME rerun.config
config['inputDir'] = inputDir
# write the config options to rerun configuration file
with open(f'{outputDir}/rerun.config', 'w') as f:
    # write the program name
    f.write(f'[{programName}]\n')
    for option in config:
        f.write(f'{option} = {config[option]}\n')
    # close the file
    f.close()

if __name__ == '__main__':
    # install the requirements
    execInstallRequirements = "pip install -r " + requirementsFile + " | { grep -v 'already satisfied' || :; }" 
    os.system(execInstallRequirements)

    # merge the dataframes
    outputFile = 'data'
    execMergeData = f'python3 {scriptDir}/mergeDf_cpsf.py {sequenceFile} {dataFile} {outputFile} {outputDir}'
    os.system(execMergeData)

    # replace the interface column
    execReplaceInterface = f'python3 {scriptDir}/replaceInterfaceColumn.py {interfaceFile} {outputDir}/{outputFile}.csv {outputFile} {outputDir}'
    os.system(execReplaceInterface)

    # split into leu and ala designs
    #execSplitDesigns = f'python3 {scriptDir}/splitDesigns_gpaCutoff.py {outputDir}/{outputFile}.csv {outputFile} {percentGpACutoff} {outputDir}'
    #os.system(execSplitDesigns)

    # make the interface pdbs figures
    #execCreatePses = f'python3 {scriptDir}/createPymolSessionFiles.py {rawDataDirAla} {optimizedPdbDir} {outputDir}/{outputFile}_ala.csv {outputDir}/interfacePdbs'
    #os.system(execCreatePses)
    execCreatePses = f'python3 {scriptDir}/createPymolSessionFiles.py {rawDataDirLeu} {optimizedPdbDir} {outputDir}/{outputFile}.csv {outputDir}/interfacePdbs'
    os.system(execCreatePses)
    
    # output pngs of the interface pdbs with hbonds and rings highlighted
    execCreatePses = f'python3 {scriptDir}/mutantInterfacePdbs.py {optimizedPdbDir} {outputDir}/{outputFile}_leu.csv {outputDir}/interfacePdbs/highlighted'
    os.system(execCreatePses)