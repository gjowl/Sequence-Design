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

# only keep sequences that where total < 0
df = df[df['Total'] < 0]

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

## separate the df into regions of interest
#dfRight = df[df['crossingAngle'] < 0]
#dfgxxxg = dfRight[dfRight['crossingAngle'] < 0]
#dfLeft = df[df['crossingAngle'] > 0]
#
## get the average energy for each region of interest
#avgEnergyRight = dfRight['Energy'].mean()
#avgEnergyGxxxg = dfgxxxg['Energy'].mean()
#avgEnergyLeft = dfLeft['Energy'].mean()
 
# what plots should I use? scatter plot for each?



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
"""
