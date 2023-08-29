import os, sys, pandas as pd, matplotlib.pyplot as plt, numpy as np

# plot scatterplot function
def plotScatterplot(df, xAxis, yAxis, outputTitle):
    # make a scatter plot of the total energy vs the percent gpa
    df.plot.scatter(x=xAxis, y=yAxis, title='Total Energy vs Percent GpA')
    # set the yAxis lower limit to 0
    #plt.ylim(bottom=0)
    #plt.ylim(top=160)

    # add in the standard deviation
    #plt.errorbar(df[xAxis], df[yAxis], yerr=df[yStd], fmt='none', ecolor='black')
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

# read in the data file
calcEnergyFile = sys.argv[1]
designEnergyFile = sys.argv[2]
outputDir = sys.argv[3]

os.makedirs(outputDir, exist_ok=True)

# read in the data files
calcEnergy_df = pd.read_csv(calcEnergyFile)
designEnergy_df = pd.read_csv(designEnergyFile)

# merge the dataframes
df = calcEnergy_df.merge(designEnergy_df, on='Sequence', how='left')

# only keep sequences with the lowest total energy
df = df.sort_values(by=['Total'], ascending=False)
df = df.drop_duplicates(subset=['Sequence'], keep='first')
# drop nan values
df = df.dropna(subset=['Design_Total'])

xAxis = 'Total'
yAxis = 'Design_Total'
plotScatterplot(df, xAxis, yAxis, 'totalEnergy')