import pandas as pd
import sys
import os
import numpy as np
from plotGeomKde import *
from functions import *
import matplotlib.pyplot as plt


'''
    This file is used to analyze the data from my second set of design runs after CHIP1.
    The goal of this analysis is to determine if this data is better than my previous runs
    by outputting graphs and statistics to a csv file. I can then compare those graphs and
    data to the previous design runs from CHIP1, aiming to have an expectation for the fluorescence
    output depending on the energies, geometry, and sequence of the protein.
'''

# Read in the data from the csv file
df = pd.read_csv(sys.argv[1])
kdeFile = os.getcwd()+'/' + '2020_09_23_kdeData.csv'

# read in kde data as a dataframe
df_kde = pd.read_csv(kdeFile)

# Set up output directory
outputDir = setupOutputDir(sys.argv[1])

# add in dimer vs monomer energy difference
df['VDWDiff'] = df['VDWDimer'] - df['VDWMonomer']
df['HBONDDiff'] = df['HBONDDimer'] - df['HBONDMonomer']
df['IMM1Diff'] = df['IMM1Dimer'] - df['IMM1Monomer']
df['VDWRepackDiff'] = df['VDWDimerRepack'] - df['VDWMonomer']
df['HBONDRepackDiff'] = df['HBONDDimerRepack'] - df['HBONDMonomer']
df['IMM1RepackDiff'] = df['IMM1DimerRepack'] - df['IMM1Monomer']
df['RepackChange'] = df['Total'] - df['firstRepackEnergy']

# sort by total energy
df = df.sort_values(by=['Total'])
df.to_csv(outputDir+'/allData.csv')

# rid of anything with Total > 0 and repack energy > 0
df = df[df['Total'] < 0]
df = df[df['VDWDimer'] < 0]

# get average repack change for each geometry number
df_avgRepack = df.groupby('geometryNumber')['RepackChange'].mean().reset_index()
print(df_avgRepack)
exit()

# how can I visualize the repack change and 

# get the top 100 sequences in Total Energy for each region
df_top = df.nsmallest(100, 'Total')

# output the top 100 sequences to a csv file
df_top.to_csv(outputDir+'/top100.csv')

# analysis of the top 100 sequences
plotGeomKde(df_kde, df, 'Total', outputDir)
plotHist(df, 'Total',outputDir, filename)

# sort the dataframes by vdwDiff plus hbondDiff using loc
df = df.sort_values(by=['VDWDiff', 'HBONDDiff'])

# the below works, but try to think of a better way to plot it to make it more visually appealing and easier to understand
plotEnergyDiffStackedBarGraph(df,outputDir)

# sort by total energy
df = df.sort_values(by=['Total'])

# output the data to a csv file
df.to_csv(outputDir+"/data.csv")

# ideas for analysis
"""
    - compare geometries from duplicate sequences
    - compare geometries from non-duplicate sequences (kde plots for this and above?)\
    - scatterplots of predicted fluorescence...?
    - overlay of kde plots for CHIP1 vs now; maybe overlay of geometries that worked in CHIP1
"""
