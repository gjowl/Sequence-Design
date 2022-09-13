import pandas as pd
import sys
import os
from plotGeomKde import *
from functions import *
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

'''
    This file is used to analyze the data from my second set of design runs after CHIP1.
    The goal of this analysis is to determine if this data is better than my previous runs
    by outputting graphs and statistics to a csv file. I can then compare those graphs and
    data to the previous design runs from CHIP1, aiming to have an expectation for the fluorescence
    output depending on the energies, geometry, and sequence of the protein.
'''

# plot histogram of dataframe and column
def plotHist(df, column, filename):
    # Plotting code below
    fig, ax = plt.subplots()
    # get the minimum and maximum values of the column
    ax.hist(df[column], bins=[-55,-50,-45,-40,-35,-30,-25,-20,-15,-10,-5], color='b')
    # set the x axis label
    ax.set_xlabel(column)
    # set the y axis label
    ax.set_ylabel('Frequency')
    # set the title
    ax.set_title(filename+' histogram')
    # save the number of data points on the figure
    ax.text(-55, 10.45, 'n = '+str(len(df)))
    # make output directory
    outputDir = os.getcwd()+'/'+filename
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)
    # save the figure
    plt.savefig(outputDir+"/histogram.png", bbox_inches='tight', dpi=150)
    plt.close()

# Read in the data from the csv file
df = pd.read_csv(sys.argv[1])
kdeFile = os.getcwd()+'/' + '2020_09_23_kdeData.csv'

# read in kde data as a dataframe
df_kde = pd.read_csv(kdeFile)

# check if VDWDiff column is all zeros
if df['VDWDiff'].sum() == 0:
    # calculate dimer vs monomer energy difference
    df['VDWDiff'] = df['VDWDimer'] - df['VDWMonomer']
    df['HBONDDiff'] = df['HBONDDimer'] - df['HBONDMonomer']
    df['IMM1Diff'] = df['IMM1Dimer'] - df['IMM1Monomer']

# only keep sequences that where total < 0
df = df[df['Total'] < -5]

# get the current working directory
cwd = os.getcwd()+"/"

# get a dataframe with sequences that are not unique
dfDup = df[df.duplicated(subset=['Sequence'], keep=False)]

# sort the dataframe by sequence and total
dfDup = dfDup.sort_values(by=['Sequence', 'Total'])
dfDup.to_csv(cwd+"duplicateSequences.csv", index=False)

# get a dataframe with sequences that are unique
dfUnique = df.drop_duplicates(subset=['Sequence'], keep='first')

# sort by total
dfUnique = dfUnique.sort_values(by=['Total'])

# output dfUnique to a csv file
dfUnique.to_csv(cwd+"uniqueSequences.csv", index=False)

# divide data into dataframes for each region
df_right = df[(df['crossingAngle'] < 0) & (df['xShift'] > 7.5)]
df_left = df[df['crossingAngle'] > 0]
df_gasright = df[(df['crossingAngle'] < 0) & (df['xShift'] < 7.5)]

# get the top 100 sequences in Total Energy for each region
df_rightTop = df_right.nsmallest(100, 'Total')
df_leftTop = df_left.nsmallest(100, 'Total')
df_gasrightTop = df_gasright.nsmallest(100, 'Total')

# add the region data to a list
df_list = [df, df_right, df_left, df_gasright, df_rightTop, df_leftTop, df_gasrightTop]
filename_list = ['All','Right', 'Left', 'GASright', 'RightTop', 'LeftTop', 'GASrightTop']

## get the average energy for each region of interest
#avgEnergyRight = dfRight['Energy'].mean()
#avgEnergyGxxxg = dfgxxxg['Energy'].mean()
#avgEnergyLeft = dfLeft['Energy'].mean()
 
# what plots should I use? scatter plot for each?
for df,filename in zip(df_list, filename_list):
    plotGeomKde(df_kde, df, 'Total', filename)
    plotHist(df, 'Total',filename)
    # sort the dataframes by vdwDiff plus hbondDiff
    df['VDW+HBOND'] = df['VDWDiff'] + df['HBONDDiff']
    df = df.sort_values(by='VDW+HBOND')
    # the below works, but try to think of a better way to plot it to make it more visually appealing and easier to understand
    plotEnergyDiffStackedBarGraph(df,filename)

# ideas for analysis
"""
    - scatterplots for each
    - histograms for top x (100?) designs; compare to previous designs in CHIP1
    - compare geometries from duplicate sequences
    - compare geometries from non-duplicate sequences (kde plots for this and above?)\
    - look at more structures
    - plots for vdw and other energy differences
    - look at the energy differences between the top 100 designs and the rest of the designs
    - scatterplots of predicted fluorescence...?
    - overlay of kde plots for CHIP1 vs now; maybe overlay of geometries that worked in CHIP1
"""
