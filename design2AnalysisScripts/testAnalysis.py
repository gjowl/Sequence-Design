import sys
import pandas as pd
import os

# read in data file
datafile = sys.argv[1]

# read in the data
df = pd.read_csv(datafile, sep='\t', header=0)

# trim data
# only keep sequences where Total Energy is less than 0
df = df[df['Total'] < 0]

# only keep sequences where VDWDiff is greater than 0
df = df[df['VDWDiff'] > 0]

# TODO: setup overlay for a list of dataframes (also get the overlays for axial and z)

# TODO: only overlay unique geometries
# TODO: compare the geometries to the sequences I got before; to the sequences that worked plot

# TODO: write code to just take in a file and output the overlay; or to just take the energy, geometry cols, and output data

# TODO: compare the energies that I get here to the older energy list (another histogram? Or some other way)
# setup overlay on map plot




# get the column names

