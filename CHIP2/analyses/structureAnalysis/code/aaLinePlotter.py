description = """
This program takes in a config file for running the amino acid line plot code. The config file options are as follows:
"""

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

# get the current directory
cwd = os.getcwd()

# gets the name of this file to access the config options
programName = getFilename(__file__)

# get the config file options
configFile = sys.argv[1]
globalConfig = read_config(configFile)
config = globalConfig[programName]

# read in the config arguments
sequenceFile = config['sequenceFile']
outputDir = config['outputDir']
codeDir = config['codeDir']
#requirementsFile = config['requirementsFile']
percentGpaCutoffs = [float(x) for x in config['percentGpaCutoffs'].split(',')]
cutoffs = [float(x) for x in config['cutoffs'].split(',')]
number_of_labels = [int(x) for x in config['number_of_labels'].split(',')]

os.makedirs(outputDir, exist_ok=True)

if __name__ == "__main__":
    # write README file 
    writeReadMe(globalConfig, outputDir)

    # install the requirements
    #execInstallRequirements = "pip install -r " + requirementsFile + " | { grep -v 'already satisfied' || :; }" 
    #os.system(execInstallRequirements)

    # execute the aaLinePlotter code
    for percentGpaCutoff, number_of_label, cutoff in zip(percentGpaCutoffs, number_of_labels, cutoffs):
        outDir = f'{outputDir}/{percentGpaCutoff}_{number_of_label}_{cutoff}'
        execAaLinePlotter = f'python3 {codeDir}/makeAALinePlot.py {sequenceFile} {outDir} {percentGpaCutoff} {number_of_label} {cutoff}'
        os.system(execAaLinePlotter)
