import os, sys, configparser, argparse
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
#inputDir   = config["inputDir"]

'''
    copy the input files into the output directory
'''
# copy the original config file to the output directory
os.system(f'cp {configFile} {outputDir}/originalConfig.config')

# copy the input files directory to the output directory
#inputDir, config = copyInputFiles(inputDir, outputDir, config) # inputDir is now the new input directory within the output directory, and config has been updated with the new file paths

'''
    reading the config file options
'''
# read in the config arguments
codeDir = config['codeDir']
clashDir = config['clashDir']
requirementsFile = config['requirementsFile']
sequenceCsv = config['sequenceCsv']
mutantCsv = config['mutantCsv']

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
        # check that 'clash' is in the directory name
        if 'clash' not in input_dir:
            continue
        # get the input directory name
        outDir = outputDir + '/' + input_dir

        # run the code to add the necessary columns to the dataframes
        sequenceFile = f'{clashDir}/{input_dir}/{sequenceCsv}'
        mutantFile = f'{clashDir}/{input_dir}/{mutantCsv}'
        print(sequenceFile, mutantFile, outDir)
        execAddColumns = f'python3 {codeDir}/addNecessaryColumns.py -seqFile {sequenceFile} -mutFile {mutantFile} -outDir {outDir}'
        os.system(execAddColumns)

        # run the voiding code if the voiding data is found in the config file
        execplotBoxplot = f'python3 {codeDir}/plotBoxplotsPerAAPosition.py {outDir}/wt.csv {outDir}/mutant.csv {outDir}'
        os.system(execplotBoxplot)

        # run boxplot code for all of the data
        execplotBoxplotCombined = f'python3 {codeDir}/plotBoxplotsCombined.py -inFile {outDir}/all.csv -outDir {outDir}'
        os.system(execplotBoxplotCombined)

        execGraphDeltaFluorescence = f'python3 {codeDir}/graphDeltaFluorescence.py -inFile {outDir}/deltaFluorescence.csv -outDir {outDir}/deltaFluorescence'
        os.system(execGraphDeltaFluorescence)