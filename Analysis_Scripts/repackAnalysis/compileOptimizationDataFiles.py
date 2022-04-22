# @Author: Gilbert Loiseau
# @Date:   2021-12-24
# @Filename: compileOptimizationDataFiles.py
# @Last modified by:   Gilbert Loiseau
# @Last modified time: 2022/03/22

"""
This searches for all of the optimizationEnergyFile.csv contained anywhere within the starting directory.
It then compiles all of them into a file for analysis by optimizedBackboneAnalysis.csv
"""

import sys
import os
import pandas as pd
import helper
from utilityFunctions import *

#Functions
def writeDataframeToNewSpreadsheet(df, outFile):
    df.to_csv(outFile, sep=',')
    print(outFile)

# Use the utilityFunctions function to get the name of this program
programName = getProgramName(sys.argv[0])
configFile = sys.argv[1]

# Read in configuration file:
globalConfig = helper.read_config(configFile)
config = globalConfig[programName]

#Config file variables
outputDir = config["outputDir"]
dataDir = config["dataDir"]
outFile = config["outFile"]

# Dataframe to save the energy files into
df = pd.DataFrame()
    
# This searches for all files within a given folder from the current directory
for root, dirs, files in os.walk(dataDir):
    if root.endswith('backboneOptimization'):
        for name in files:
            if name.endswith(("optimizationEnergyFile", ".csv")):
                filename = root + "/" + name
                #In my original outputs, I used grep -r "Backbone Optimization:" to compile my data. I rid of those with the below
                tmpDf = pd.read_csv(filename, sep="[:\t]", engine='python')
                tmpDf.reset_index(drop=True, inplace=True)
                df = df.append(tmpDf)

writeDataframeToNewSpreadsheet(df, outFile)
