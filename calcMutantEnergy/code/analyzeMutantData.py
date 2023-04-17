import os, sys, pandas as pd
import matplotlib.pyplot as plt

# read the command line arguments
input_file = sys.argv[1]

# read the input file as a dataframe
df = pd.read_csv(input_file, sep=',', dtype={'Interface': str})

column = 'Region'

# loop through the regions
for value in df[column].unique():
    # get the interface dataframe
    value_df = df[df[column] == value]
    # plot a histogram of counts for each position
    plt.hist(value_df['Position'], bins=range(1,19), align='left')
    # set the title
    plt.title(f'{value} mutant count per position')
    # set the x and y labels
    plt.xlabel('Position')
    plt.ylabel('Count')
    # adjust the x axis
    plt.xticks(range(1,19))
    # save the figure
    plt.savefig(f'{value}.png')
    # clear the figure
    plt.clf()