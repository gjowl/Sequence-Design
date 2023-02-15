import os, sys, pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# read in the data file
dataFile = sys.argv[1]
df = pd.read_csv(dataFile)

# get the output directory
outputDir = sys.argv[2]

# only keep sequences with the lowest total energy
df = df.sort_values(by=['Total'])
df = df.drop_duplicates(subset=['Sequence'], keep='first')

# rid of any sequences where the PercentStd > 10
df = df[df['PercentStd'] < 10]

# make a scatter plot of the total energy vs the percent gpa
df.plot.scatter(x='Total', y='PercentGpA', title='Total Energy vs Percent GpA')

# add in the standard deviation
plt.errorbar(df['Total'], df['PercentGpA'], yerr=df['PercentStd'], fmt='none', ecolor='black')
plt.text(0.99, 1.10, f'N = {len(df)}', transform=plt.gca().transAxes, fontsize=14, verticalalignment='top', horizontalalignment='right')
plt.savefig(f'{outputDir}/scatter.png')

# add a line of best fit and an r^2 value
m, b = np.polyfit(df['Total'], df['PercentGpA'], 1)
plt.plot(df['Total'], m*df['Total'] + b, color='red')

# add the r^2 value to the top left of the plot
r2 = np.corrcoef(df['Total'], df['PercentGpA'])[0,1]**2
plt.text(0.01, 1.10, f'r^2 = {r2:.2f}', transform=plt.gca().transAxes, fontsize=14, verticalalignment='top')
plt.savefig(f'{outputDir}/scatterRegression.png')