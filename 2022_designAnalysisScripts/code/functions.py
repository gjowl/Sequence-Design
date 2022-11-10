import pandas as pd
import numpy as np
import os
import configparser

def setupOutputDir(inputFile):
    '''
        This function creates the output directory for the analysis.
    '''
    # get directory of the input file
    inputDir = os.path.dirname(inputFile)
    if inputDir == '':
        inputDir = os.getcwd()

    # make output directory named after the input file
    outputDir = inputDir + '/' + os.path.basename(inputFile).split('.')[0]
    # check if the analysis directory exists
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)
    return outputDir

def parseDf(df, energyCutoff):
    '''
        This function gets rid of any duplicate sequences and keeps sequences with
        an energy score less than the cutoff.
    '''
    # get a dataframe with sequences that are unique
    df = df.drop_duplicates(subset=['Sequence'], keep='first')
    
    # check if there is a column with percent GpA
    if 'PercentGpA' in df.columns:
        # only use data with PercentGpa > 50
        df = df[df['PercentGpa'] < 50]

    # only keep sequences where total < energyCutoff
    df = df[df['Total'] < energyCutoff]
    return df

# Helper file for reading the config file of interest for running the program
def read_config(configFile):
    config = configparser.ConfigParser()
    config.read(configFile)
    return config
