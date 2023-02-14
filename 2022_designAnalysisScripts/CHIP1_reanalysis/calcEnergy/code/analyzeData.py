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

# rid of any sequences where the PercentStd > 10 and greater than 0
df = df[df['PercentGpaStdDev'] < 10]
df = df[df['PercentGpaStdDev'] > 0]

# sort the df by the percent gpa
df = df.sort_values(by=['PercentGpa'])

# make a histogram of percent gpa on the y axis and sequence on the x axis
df.plot.bar(x='Sequence', y='PercentGpa', title='Percent GpA', color='lightskyblue')
plt.ylim(0, 120)

# change the color of the bars to red if angle < 0
for i, row in df.iterrows():
    if row['endCrossingAngle'] < 0:
        plt.gca().get_children()[i].set_color('red')

# add the standard deviation
plt.errorbar(df['Sequence'], df['PercentGpa'], yerr=df['PercentGpaStdDev'], fmt='none', ecolor='black')
plt.savefig(f'{outputDir}/hist_PercentGpA.png')

# rid of any sequences where the PercentGpa < 40 (G83I)
df_G83I = df[df['PercentGpa'] > 40]

# rid of any sequences where the PercentGpa < 45 (G83I+10, somewhat arbitrary in terms of dimerization or not)
df_G83I_dimer = df[df['PercentGpa'] > 45]

# add all dfs to a list
dfs = [df, df_G83I, df_G83I_dimer]

# make a list of names for the dfs
dfsNames = ['All', 'G83I', 'LikelyDimer']

# loop through the dfs and make plots
for df, name in zip(dfs, dfsNames):
    # define the output directory
    outDir = f'{outputDir}/{name}'

    # make an output directory for the plots
    os.makedirs(outDir, exist_ok=True)

    
    # make a scatter plot of the total energy vs the percent gpa
    df.plot.scatter(x='Total', y='PercentGpa', title='Total Energy vs Percent GpA')

    # set the y axis to be between 0 and a tens place near the max
    plt.ylim(0, int(df['PercentGpa'].max()/10)*10+20)

    # add in the standard deviation
    plt.errorbar(df['Total'], df['PercentGpa'], yerr=df['PercentGpaStdDev'], fmt='none', ecolor='black')
    plt.text(0.99, 1.10, f'N = {len(df)}', transform=plt.gca().transAxes, fontsize=14, verticalalignment='top', horizontalalignment='right')
    plt.savefig(f'{outDir}/scatter_EnergyVsPercentGpA.png')

    # add a line of best fit and an r^2 value
    m, b = np.polyfit(df['Total'], df['PercentGpa'], 1)
    plt.plot(df['Total'], m*df['Total'] + b, color='red')

    # add the r^2 value to the top left above the plot
    r2 = np.corrcoef(df['Total'], df['PercentGpa'])[0,1]**2
    plt.text(0.01, 1.10, f'r^2 = {r2:.2f}', transform=plt.gca().transAxes, fontsize=14, verticalalignment='top')
    plt.savefig(f'{outDir}/scatter_regression.png')

    # output the df to a csv file
    df.to_csv(f'{outDir}/totalEnergyVsPercentGpA.csv')

    # reset the plot
    plt.clf()