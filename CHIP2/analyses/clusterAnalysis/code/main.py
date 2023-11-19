import os, sys
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
input_file = config['input_file']
output_dir = config['output_dir']
cluster_script = config['cluster_script']
regression_script = config['regression_script']
cluster_cols = config['cluster_cols']

# get the name of the input file
input_file_name = os.path.splitext(input_file)[0]
input_file_name = os.path.basename(input_file_name)

if __name__ == "__main__":
    # execute the cluster script
    execCluster = f'python3 {cluster_script} {input_file} {output_dir} {cluster_cols}' 
    os.system(execCluster)

    # execute the regression script
    execRegression = f'python3 {regression_script} {output_dir}/{input_file_name}_clusters.csv {output_dir}'
    os.system(execRegression)