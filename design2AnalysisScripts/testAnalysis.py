import sys
import pandas as pd
import os
from plotGeomKde import *

# read in data file
datafile = sys.argv[1]
kdeFile = os.getcwd()+'/' + '2020_09_23_kdeData.csv'

# read in the data
df_data = pd.read_csv(datafile, sep=',', header=0)
df_kde = pd.read_csv(kdeFile)

# trim data
# only keep sequences where Total Energy is less than 0
print(df_data)
df_total = df_data[df_data['Total'] < 0]

# only keep sequences where VDWDiff is greater than 0
df_vdwDiff = df_data[df_data['VDWDiff'] > 0]

df_list = [df_data]
# TODO: setup overlay for a list of dataframes (also get the overlays for axial and z)
for df in df_list:
    plotGeomKde(df_kde, df)
# TODO: only overlay unique geometries
# TODO: compare the geometries to the sequences I got before; to the sequences that worked plot

# TODO: write code to just take in a file and output the overlay; or to just take the energy, geometry cols, and output data

# TODO: compare the energies that I get here to the older energy list (another histogram? Or some other way)
# setup overlay on map plot




# get the column names

