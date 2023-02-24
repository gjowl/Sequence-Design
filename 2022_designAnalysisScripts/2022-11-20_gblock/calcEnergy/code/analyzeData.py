import os, sys, pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# plot scatterplot function
def plotScatterplot(df, xAxis, yAxis, yStd, outputTitle):
    # make a scatter plot of the total energy vs the percent gpa
    df.plot.scatter(x=xAxis, y=yAxis, title='Total Energy vs Percent GpA')
    # set the yAxis lower limit to 0
    plt.ylim(bottom=0)
    plt.ylim(top=160)

    # add in the standard deviation
    plt.errorbar(df[xAxis], df[yAxis], yerr=df[yStd], fmt='none', ecolor='black')
    plt.text(0.99, 1.10, f'N = {len(df)}', transform=plt.gca().transAxes, fontsize=14, verticalalignment='top', horizontalalignment='right')
    plt.savefig(f'{outputDir}/scatter_{outputTitle}.png')

    # add a line of best fit and an r^2 value
    m, b = np.polyfit(df[xAxis], df[yAxis], 1)
    plt.plot(df[xAxis], m*df[xAxis] + b, color='red')

    # add the r^2 value to the top left of the plot
    r2 = np.corrcoef(df[xAxis], df[yAxis])[0,1]**2
    plt.text(0.01, 1.10, f'r^2 = {r2:.2f}', transform=plt.gca().transAxes, fontsize=14, verticalalignment='top')
    plt.savefig(f'{outputDir}/scatterRegression_{outputTitle}.png')
    plt.clf()

def addEnergyDifferencesToDataframe(df, cols):
    for col in cols:
        df[f'{col}Diff'] = df[f'{col}DimerOptimize'] - df[f'{col}Monomer']
    return df

# read in the data file
dataFile = sys.argv[1]
df = pd.read_csv(dataFile)

# get the output directory
outputDir = sys.argv[2]

# only keep sequences with the lowest total energy
df = df.sort_values(by=['Total'])
df = df.drop_duplicates(subset=['Sequence'], keep='first')

# rid of any sequences where the PercentStd > 10
df = df[df['PercentStd'] < 15]

# add energy differences to the dataframe
cols = ['VDW', 'HBOND', 'IMM1']
df = addEnergyDifferencesToDataframe(df, cols)

# only plot the sequences with the HBONDDiff > 5
lowHbond_df = df[df['HBONDDiff'] > -5]
# save the lowHbond_df to a csv file
lowHbond_df.to_csv(f'{outputDir}/lowHbond_df.csv', index=False)

# make list of dfs to plot
df_list = [df, lowHbond_df]
outputTitle_list = ['TotalEnergy', 'LowHbond']

for df,title in zip(df_list, outputTitle_list):
    plotScatterplot(df, 'Total', 'PercentGpA', 'PercentStd', title)