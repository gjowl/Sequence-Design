import os, sys, pandas as pd
import matplotlib.pyplot as plt

# read the command line arguments
input_file = sys.argv[1]
data_file = sys.argv[2]
output_file = sys.argv[3]

# read the input file as a dataframe
df = pd.read_csv(input_file, sep=',')
# read the data file as a dataframe
data_df = pd.read_csv(data_file, sep=',')

# merge the dataframes by the Mutant column and remove any columns that are duplicated
df = pd.merge(df, data_df, on='Mutant')

# output the dataframe to a csv file without the index
df.to_csv(output_file, index=False)

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