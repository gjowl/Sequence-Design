import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

"""
This script will analyze the data from the toxgreen assay against the design data.
    - make graphs: energy vs fluorescence, energy vs interface, etc.
    - ...
"""

# get the input data from command line
toxData = sys.argv[1]
designData = sys.argv[2]

# read in the data to a dataframe
toxDf = pd.read_csv(toxData)
designDf = pd.read_csv(designData)

# might be easiest to setup the names for the toxgreen data to match the design data into a dataframe and just add to the dataframe
# make a map of the sample name to the fluorescence value
toxMap = {}
for i in range(len(toxDf)):
    toxMap[toxDf['Sample'][i]] = toxDf['Fluorescence'][i]