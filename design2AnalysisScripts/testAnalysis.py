import sys
import pandas as pd
import os
from plotGeomKde import *
from functions import *

# plot histogram of dataframe and column
def plotHist(df, column):
    plt.hist(df[column], bins=10)
    plt.savefig(os.getcwd()+"/"+column+"_test.png", bbox_inches='tight', dpi=150)

# read in data file
datafile = sys.argv[1]
kdeFile = os.getcwd()+'/' + '2020_09_23_kdeData.csv'

# read in the data
df_data = pd.read_csv(datafile, sep=',', header=0)
df_kde = pd.read_csv(kdeFile)

# calculate dimer vs monomer energy difference
df_data['VDWDiff'] = df_data['VDWDimer'] - df_data['VDWMonomer']
df_data['HBONDDiff'] = df_data['HBONDDimer'] - df_data['HBONDMonomer']
df_data['IMM1Diff'] = df_data['IMM1Dimer'] - df_data['IMM1Monomer']

# trim data
# only keep sequences where Total Energy is less than 0
df_total = df_data[df_data['Total'] < 0]

# only keep sequences where VDWDiff is greater than 0
df_vdwDiff = df_total[df_total['VDWDiff'] < 0]

df_list = [df_total, df_vdwDiff]

# divide data into dataframes for each region
df_right = df_vdwDiff[df_vdwDiff['crossingAngle'] < 0]
df_left = df_vdwDiff[df_vdwDiff['crossingAngle'] > 0]
df_gasright = df_vdwDiff[df_vdwDiff['crossingAngle'] < 0 & df_vdwDiff['xShift'] < -7.5]

# add the region data to a list
df_list = [df_right, df_left, df_gasright]

# TODO: setup overlay for a list of dataframes (also get the overlays for axial and z)
for df in df_list:
    plotGeomKde(df_kde, df, 'Total')
    plotHist(df, 'Total')
    # the below works, but try to think of a better way to plot it to make it more visually appealing and easier to understand
    plotEnergyDiffStackedBarGraph(df)

# output updated df_data to csv
df_data.to_csv(os.getcwd()+"/test.csv", index=False)

# TODO: only overlay unique geometries
# TODO: compare the geometries to the sequences I got before; to the sequences that worked plot

# TODO: compare the energies that I get here to the older energy list (another histogram? Or some other way)
# TODO: get the frequency of each aa at each position (I have code for this somewhere, add it here)
# setup overlay on map plot




# get the column names

