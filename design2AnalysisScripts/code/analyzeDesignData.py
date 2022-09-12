import pandas as pd
import sys
import os

'''
    This file is used to analyze the data from my second set of design runs after CHIP1.
    The goal of this analysis is to determine if this data is better than my previous runs
    by outputting graphs and statistics to a csv file. I can then compare those graphs and
    data to the previous design runs from CHIP1, aiming to have an expectation for the fluorescence
    output depending on the energies, geometry, and sequence of the protein.
'''

# Read in the data from the csv file
df = pd.read_csv(sys.argv[1])

# get a dataframe with sequences that are not unique
dfDup = df[df.duplicated(subset=['Sequence'], keep=False)]

# get a dataframe with sequences that are unique
dfUnique = df.drop_duplicates(subset=['Sequence'], keep='first')

# separate the df into regions of interest
dfRight = df[df['crossingAngle'] < 0]
dfgxxxg = dfRight[dfRight['crossingAngle'] < 0]
dfLeft = df[df['crossingAngle'] > 0]

# get the average energy for each region of interest
avgEnergyRight = dfRight['Energy'].mean()
avgEnergyGxxxg = dfgxxxg['Energy'].mean()
avgEnergyLeft = dfLeft['Energy'].mean()
 
# what plots should I use? scatter plot for each?
