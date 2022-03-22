# @Author: Gilbert Loiseau
# @Date:   2022/03/18
# @Filename: helper.py
# @Last modified by:   Gilbert Loiseau
# @Last modified time: 2022/03/21

"""
Helper file for reading the config file of interest for running the programs in runDesignAndMakeCHIP
"""

import configparser

# Method to read config file settings
# configFile is the path the the config file of choice
def read_config(configFile):
    config = configparser.ConfigParser()
    config.read(configFile)
    return config
