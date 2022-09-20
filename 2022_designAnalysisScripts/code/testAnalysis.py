import sys
import pandas as pd
import os
from plotGeomKde import *
from functions import *
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

# plot histogram of dataframe and column
def plotHist(df, column, filename):
    plt.ylim(0, 0.5)
    plt.xlim(-45,-5)
    plt.hist(df[column], weights=np.ones(len(df))/len(df), bins=[-45,-40,-35,-30,-25,-20,-15,-10,-5])
    plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
    # set the y axis label
    plt.ylabel('Frequency')
    # set the x axis label
    plt.xlabel('Energy Score')
    # set the title
    plt.title(filename+' histogram')
    # save the number of data points on the figure
    plt.text(-44, 0.45, 'n = '+str(len(df)))
    plt.savefig(os.getcwd()+"/"+column+"_"+filename+".png", bbox_inches='tight', dpi=150)
    plt.close()

# read in data file
datafile = sys.argv[1]
kdeFile = os.getcwd()+'/' + '2020_09_23_kdeData.csv'

# read in the data
df_data = pd.read_csv(datafile, sep=',', header=0)
df_kde = pd.read_csv(kdeFile)

# check if VDWDiff column is all zeros
if df_data['VDWDiff'].sum() == 0:
    # calculate dimer vs monomer energy difference
    df_data['VDWDiff'] = df_data['VDWDimer'] - df_data['VDWMonomer']
    df_data['HBONDDiff'] = df_data['HBONDDimer'] - df_data['HBONDMonomer']
    df_data['IMM1Diff'] = df_data['IMM1Dimer'] - df_data['IMM1Monomer']

# trim data
# only keep sequences where Total Energy is less than 0
df_total = df_data[df_data['Total'] < -5]

<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
#df_total = df_total[df_total['PercentGpa'] < 50]
=======
df_total = df_total[df_total['PercentGpa'] > 50]
>>>>>>> 79960644233ca4e4fae65934702dc00ff55bf9de
=======
df_total = df_total[df_total['PercentGpa'] > 50]
>>>>>>> 79960644233ca4e4fae65934702dc00ff55bf9de
=======
df_total = df_total[df_total['PercentGpa'] > 50]
>>>>>>> 79960644233ca4e4fae65934702dc00ff55bf9de
=======
df_total = df_total[df_total['PercentGpa'] < 50]
>>>>>>> ad76af7087793a7c3c58fcc8c653ea5605f2b2ff
=======
df_total = df_total[df_total['PercentGpa'] < 50]
>>>>>>> ad76af7087793a7c3c58fcc8c653ea5605f2b2ff
=======
df_total = df_total[df_total['PercentGpa'] < 50]
>>>>>>> ad76af7087793a7c3c58fcc8c653ea5605f2b2ff
=======
df_total = df_total[df_total['PercentGpa'] < 50]
>>>>>>> 526550a3041fc0669e9d118b0c727dbcc999064b
=======
df_total = df_total[df_total['PercentGpa'] < 50]
>>>>>>> aff5e515ed04cfd4d742cd0dd2b778f297359cb8
df_total = df_total.sort_values(by='VDWDiff')
# only keep sequences where VDWDiff is greater than 0
df_vdwDiff = df_total[df_total['VDWDiff'] < 0]

# divide data into dataframes for each region
df_right = df_vdwDiff[(df_vdwDiff['crossingAngle'] < 0) & (df_vdwDiff['xShift'] > 7.5)]
df_left = df_vdwDiff[df_vdwDiff['crossingAngle'] > 0]
df_gasright = df_vdwDiff[(df_vdwDiff['crossingAngle'] < 0) & (df_vdwDiff['xShift'] < 7.5)]

# sort the dataframes by vdwDiff
#df_total = df_total.sort_values(by='Total')
#df_total = df_total[df_total['StartSequence'] == df['Sequence']] 

# add the region data to a list
df_list = [df_total, df_right, df_left, df_gasright]
filename_list = ['All','Right', 'Left', 'GASright']

# TODO: setup overlay for a list of dataframes (also get the overlays for axial and z)
for df,filename in zip(df_list, filename_list):
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
    #plotGeomKde(df_kde, df, 'Total')
    #plotHist(df, 'Total',filename)
=======
    plotGeomKde(df_kde, df, 'Total')
    plotHist(df, 'Total',filename)
>>>>>>> ad76af7087793a7c3c58fcc8c653ea5605f2b2ff
=======
    plotGeomKde(df_kde, df, 'Total')
    plotHist(df, 'Total',filename)
>>>>>>> ad76af7087793a7c3c58fcc8c653ea5605f2b2ff
=======
    plotGeomKde(df_kde, df, 'Total')
    plotHist(df, 'Total',filename)
>>>>>>> ad76af7087793a7c3c58fcc8c653ea5605f2b2ff
=======
    plotGeomKde(df_kde, df, 'Total')
    plotHist(df, 'Total',filename)
>>>>>>> 526550a3041fc0669e9d118b0c727dbcc999064b
=======
    plotGeomKde(df_kde, df, 'Total')
    plotHist(df, 'Total',filename)
>>>>>>> aff5e515ed04cfd4d742cd0dd2b778f297359cb8
    # the below works, but try to think of a better way to plot it to make it more visually appealing and easier to understand
    plotEnergyDiffStackedBarGraph(df,filename)

#df_total = df_total[df_total['PercentGpa'] > 60]
#plotGeomKde(df_kde, df_total, 'PercentGpa')

# output updated df_data to csv
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
df_data.to_csv(os.getcwd()+"/test.csv", index=False)
=======
#df_data.to_csv(os.getcwd()+"/test.csv", index=False)
>>>>>>> 79960644233ca4e4fae65934702dc00ff55bf9de
=======
#df_data.to_csv(os.getcwd()+"/test.csv", index=False)
>>>>>>> 79960644233ca4e4fae65934702dc00ff55bf9de
=======
#df_data.to_csv(os.getcwd()+"/test.csv", index=False)
>>>>>>> 79960644233ca4e4fae65934702dc00ff55bf9de
=======
#df_data.to_csv(os.getcwd()+"/test.csv", index=False)
>>>>>>> ad76af7087793a7c3c58fcc8c653ea5605f2b2ff
=======
#df_data.to_csv(os.getcwd()+"/test.csv", index=False)
>>>>>>> ad76af7087793a7c3c58fcc8c653ea5605f2b2ff
=======
#df_data.to_csv(os.getcwd()+"/test.csv", index=False)
>>>>>>> ad76af7087793a7c3c58fcc8c653ea5605f2b2ff
=======
#df_data.to_csv(os.getcwd()+"/test.csv", index=False)
>>>>>>> 526550a3041fc0669e9d118b0c727dbcc999064b
=======
#df_data.to_csv(os.getcwd()+"/test.csv", index=False)
>>>>>>> aff5e515ed04cfd4d742cd0dd2b778f297359cb8

# TODO: only overlay unique geometries
# TODO: compare the geometries to the sequences I got before; to the sequences that worked plot

# TODO: compare the energies that I get here to the older energy list (another histogram? Or some other way)
# TODO: get the frequency of each aa at each position (I have code for this somewhere, add it here)
# setup overlay on map plot




# get the column names

