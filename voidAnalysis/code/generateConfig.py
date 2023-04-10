"""
Example code for generating a configuration file for ngsAnalysis
"""
import os
import configparser

# input directories
root_dir = os.getcwd()
#raw_data_dir = '2023-3-7_leuCHIP_mutants_rerun'
raw_data_dir = '2023-3-13_alaCHIP_mutants_rerun'
#raw_data_dir = 'CHIP1_data'
#data_dir = f'/mnt/d/DesignRuns/{raw_data_dir}'
data_dir = f'/home/loiseau@ad.wisc.edu/Downloads/{raw_data_dir}'
config_dir = f'{root_dir}/config'

# make the config directory if it doesn't exist
os.makedirs(config_dir, exist_ok=True)

# create config file object
config_file = configparser.ConfigParser()
configFile = f'{config_dir}/{raw_data_dir}.config'

# set up directory structure
curr_dir = os.getcwd()

# define the analysis being performed
analysis = 'void'

# input files
design_data_file_name = 'CHIPSeqs_ala.csv'
design_data_file = f'{curr_dir}/{design_data_file_name}'

# output
compile_file = f'{raw_data_dir}_{analysis}_compiled.csv'
delimiter = ','
file_to_compile = 'sasaMap.txt'
appended_file = f'{raw_data_dir}_{analysis}_extended.csv'
one_hot_file = f'{raw_data_dir}_{analysis}_interface_mutants.csv'
analyze_file = f'{raw_data_dir}_{analysis}_CHIP2Seqs.csv'
output_dir = f'{curr_dir}/{raw_data_dir}_{analysis}'
one_hot_columns = 'Mutant Sequence'

# main code section
config_file["main"]={
    "design_data_file": design_data_file,
    "raw_data_dir": data_dir,
    "compile_file": compile_file,
    "file_to_compile": file_to_compile,
    "delimiter": delimiter,
    "appended_file": appended_file,
    "one_hot_file": one_hot_file,
    "one_hot_columns": one_hot_columns,
    "analyze_file": analyze_file,
    "output_dir": output_dir,
}

# SAVE CONFIG FILE
with open(configFile, 'w+') as configfileObj:
    config_file.write(configfileObj)
    configfileObj.flush()
    configfileObj.close()

print("Config file "+configFile+" created")

# PRINT FILE CONTENT
read_file = open(configFile, "r")
content = read_file.read()
print("Content of the config file are:\n")
print(content)
read_file.flush()
read_file.close()