import sys

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



if __name__ == '__main__':
    # untar the files
    execUntar = f'python3 {untarScript} {inputDir}'
    os.system(execUntar)

    # add the pdb files to the output directory
    execAddPdbs = f'python3 {addPdbsScript} {inputDir}'
    os.system(execAddPdbs)

    # create the csv file
    execCreateCsv = f'python3 {createCsvScript} {inputDir} {csvFile}'
    os.system(execCreateCsv)
