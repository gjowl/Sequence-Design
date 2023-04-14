import configparser
import os
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
output_dir = config['output_dir']
raw_data_dir = config['raw_data_dir']
design_data_file = config['design_data_file']
compile_file = config['compile_file']
delimiter = config['delimiter']
file_to_compile = config['file_to_compile']
appended_file = config['appended_file']
one_hot_file = config['one_hot_file']
analyze_file = config['analyze_file']
output_dir = config['output_dir']
one_hot_columns = config['one_hot_columns'] 
polyAla_file = config['polyAla_file']

# make the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

if __name__ == "__main__":
    # compile the files
    exec_compile = f'python3 code/compileFiles.py {raw_data_dir} {output_dir} {compile_file} {file_to_compile} {delimiter}'
    os.system(exec_compile)

    # use append the design data to the data file
    exec_append_data = f'python3 code/appendDesignData.py {output_dir}/{compile_file} {design_data_file} {appended_file} {output_dir}'
    os.system(exec_append_data)

    # use one-hot encoding to only keep mutants with mutations at the interface
    exec_one_hot = f'python3 code/oneHotEncode.py {output_dir}/{appended_file} {one_hot_file} {output_dir} {one_hot_columns}'
    os.system(exec_one_hot)

    # analyze the data
    exec_analyze = f'python3 code/voidIdeaFromAlessandro.py {output_dir}/{one_hot_file} {polyAla_file} {analyze_file} {output_dir}'
    os.system(exec_analyze)
