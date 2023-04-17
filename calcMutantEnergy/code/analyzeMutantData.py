import os, sys, pandas as pd
import matplotlib.pyplot as plt

# read the command line arguments
input_file = sys.argv[1]

# read the input file as a dataframe
df = pd.read_csv(input_file, sep=',')

# keep sequences that don't match the directory name
df = df[df['Sequence'] != df['Directory']]

# get the Total energy by subtracting the Dimer from the Monomer
df['Total'] = df['Dimer'] - df['Monomer']

# get the range of Dimer values
dimer_max = df['Total'].max()
dimer_min = df['Total'].min()

print(dimer_max, dimer_min)
