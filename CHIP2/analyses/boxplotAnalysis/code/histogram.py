import os, sys, pandas as pd
import matplotlib.pyplot as plt

# read the command line arguments
input_file = sys.argv[1]

# get the name of the input file
input_name = input_file.split('/')[-1].split('.')[0]

# read the input file as a dataframe
df = pd.read_csv(input_file, sep=',', dtype={'Interface': str})

# make a histogram of the total energies
df['Total'].hist(bins=15)
# output the histogram
plt.savefig(f'{input_name}_hist.png')