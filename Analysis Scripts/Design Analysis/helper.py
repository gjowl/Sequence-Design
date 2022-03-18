"""
Helper file for reading the config file of interest for running the programs in runDesignAndMakeCHIP
"""

import configparser

# Method to read config file settings
def read_config():
    config = configparser.ConfigParser()
    config.read('analysis.config')
    return config
