import os, sys, pandas as pd
import matplotlib.pyplot as plt
import sklearn.

"""
This script analyzes the score files in the output directory and outputs a csv file with the data.
"""

# get the input directory from the command line
scoreFile = sys.argv[1]
outputDir = sys.argv[2]

# make the output directory if it doesn't exist
os.makedirs(outputDir, exist_ok=True)

# read in the score file as a dataframe
scoreData = pd.read_csv(scoreFile, sep=',', header=0) 

# sort the data by rms
scoreData = scoreData.sort_values(by=['rms'])

# get the number of sequences with an rms less than 3.0
rmsLessThan3 = scoreData[scoreData['rms'] < 3.0]
print(f'The number of sequences with an rms less than 3.0 is {len(rmsLessThan3)}')

# create a scatter plot of the rms vs the interface score

# TODO:
# - add in scatter plot function
# - decide other things to analyze and make plots for
# - get the average interface score and rmsd for the top x sequences
# - maybe average score for the top x sequences against msl score?

