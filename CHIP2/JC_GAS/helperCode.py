import os, configparser

'''
    functions
'''
# Method to read config file settings
# Helper file for reading the config file of interest for running the program
def read_config(configFile):
    config = configparser.ConfigParser()
    config.read(configFile)
    return config

# get filename separate from type and directory
def getFilename(file):
    programPath = os.path.realpath(file)
    programDir, programFile = os.path.split(programPath)
    filename, programExt = os.path.splitext(programFile)
    return filename

# copy the input files directory to the output directory
def copyInputFiles(inputDir, outputDir, config):
    # check if the input files directory exists
    newInputDir = f'{outputDir}/inputFiles'
    os.makedirs(newInputDir, exist_ok=True)
    # copy the input files to the new input directory
    for option in config:
        if 'file' in option.lower():
            file = config[option]
            # check if the file exists in the new input directory
            if not os.path.exists(f'{newInputDir}/{file}'):
                # check if the file is a path (a file from another directory)
                if os.path.exists(file):
                    os.system(f'cp {file} {newInputDir}')
                    # replace the config file option with the new path
                    filename = getFilename(file) + os.path.splitext(file)[1]
                    # update the config file option with the updated filename
                    config[option] = filename
                else:
                    inputFile = f'{inputDir}/{file}'
                    os.system(f'cp {inputFile} {newInputDir}')
    # rename the input directory to the new input directory
    return newInputDir, config

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

# create a tarball of the scripts and delete the directory
#def copyScripts(scriptDir, outputDir, programName, config):
#    scriptOutputDir = f'{outputDir}/scripts'
#    os.makedirs(scriptOutputDir, exist_ok=True)
#    for option in config:
#        if 'script' in option.lower():
#            script = config[option]
#            # check if the file is a path (a script from another directory)
#            if os.path.exists(script):
#                os.system(f'cp {script} {scriptOutputDir}')
#                # replace the config file option with the path to the script
#                filename = getFilename(script) + os.path.splitext(script)[1]
#            else:
#                inputFile = f'{scriptDir}/{script}'
#                os.system(f'cp {inputFile} {scriptOutputDir}')
#    # copy the driver script to the output directory
#    os.system(f'cp {scriptDir}/{programName}.py {scriptOutputDir}')
#    # tar the scriptOutputDir and delete the directory (to save space)
#    os.system(f'tar -cvf {outputDir}/scripts.tar.gz {scriptOutputDir}/*')
#    os.system(f'rm -r {scriptOutputDir}')
