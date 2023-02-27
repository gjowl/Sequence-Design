import os, sys, pandas as pd
from classes.df_handler import df_handler

# read in the data to a dataframe
toxDf = pd.read_csv(sys.argv[1])
designDf = pd.read_csv(sys.argv[2])
interfaceFile = sys.argv[3]

# append the columms from the toxgreen data to the design data
for col in toxDf.columns:
    designDf[col] = toxDf[col]

# make a graph of the energy vs fluorescence
plt.scatter(designDf['Energy'], designDf['Fluorescence'])
plt.xlabel('Energy')
plt.ylabel('Fluorescence')
plt.title('Energy vs Fluorescence')

# I have code for the below, just need to add it in
# TODO: get sequences that match certain interfaces
# TODO: analyze the data for each interface
# TODO: make a graph of the energy per interface