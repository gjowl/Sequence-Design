import sys
import os
import pandas as pd
from difflib import SequenceMatcher

"""
Run as:
    python3 checkForHomodimerSequences.py [inputFile]

This code is used to extract homodimer sequences from my original backbone search dataset.
"""

#MAIN
# variables: if want to make this more multipurpose, add the below into a config file
outputDir = os.getcwd()+'/'

# read in input file from command line file options
inputFile = sys.argv[1]
df = pd.read_csv(inputFile)


# check if both sequences are the same
df = df[df['Sequence 1'] == df['Sequence 2']]
# check if the aligned sequence 1 and 2 have at least 80% similarity
df = df[df['Aligned Seq 1'] == df['Aligned Seq 2']]

# check if axial distance is greater than 6
df = df[df['Axial distance'] > 6]
# check if the angle is between -90 and 90
df = df[df['Angle'] > -90]
df = df[df['Angle'] < 90]

# output the dataframe
df.to_csv(outputDir+'homodimerSequences.csv', index=False)