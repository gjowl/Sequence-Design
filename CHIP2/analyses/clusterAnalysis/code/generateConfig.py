"""
Example code for generating a configuration file for ngsAnalysis
"""
import os
import configparser

# input directories
root_dir = os.getcwd()
#dir_to_analyze = '2023-3-7_leuDesigns'
dir_to_analyze = '2023-3-13_alaDesigns'
#dir_to_analyze = 'CHIP1_data'
data_dir = f'/mnt/d/github/Sequence-Design/2023_designData/{dir_to_analyze}'
#data_dir = f'/mnt/d/github/Sequence-Design/CHIP1_reanalysis/calcEnergy/{dir_to_analyze}'
config_dir = f'{root_dir}/config'

# make the config directory if it doesn't exist
os.makedirs(config_dir, exist_ok=True)

# create config file object
config_file = configparser.ConfigParser()
configFile = f'{config_dir}/{dir_to_analyze}.config'

# set up directory structure
curr_dir = os.getcwd()

# input files
input_file = f'{data_dir}/allData.csv'

# scripts
script_dir = f'{curr_dir}/code'
script1 = f'{script_dir}/clusterPipeline.py'
script2 = f'{script_dir}/linearRegression.py'

# output
output_dir = f'{curr_dir}/{dir_to_analyze}'

cluster_cols = 'endXShift,endCrossingAngle,endAxialRotation,endZShift,VDWDiff,HBONDDiff,IMM1Diff,Total'

# main code section
config_file["main"]={
    "input_file": input_file,
    "output_dir": output_dir,
    "cluster_script": script1,
    "regression_script": script2,
    "cluster_cols": cluster_cols,
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