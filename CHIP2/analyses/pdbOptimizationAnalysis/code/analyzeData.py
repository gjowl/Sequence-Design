import os, sys, pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np

colors = ['mediumseagreen', 'moccasin', 'darkslateblue', 'brown', 'pink', 'gray', 'olive', 'cyan']
# plot scatterplot function
#TODO: could get a standard deviation for the x axis energies now that I have multiple repack energies
def plotScatterplot(df, xAxis, yAxis, yStd, regression_degree, output_title, output_dir, sampleType=0, color=0):
    for sample, i in zip(df['Sample'].unique(), range(len(df['Sample'].unique()))):
        df_sample = df[df['Sample'] == sample]
        # plot the WT sequence fluorescence vs the energy
        plt.scatter(df_sample[xAxis], df_sample[yAxis], color=colors[i], label=sample, s=5)
        # plot the standard deviation
        plt.errorbar(df_sample[xAxis], df_sample[yAxis], yerr=df_sample[yStd], fmt='o', color=colors[i], ecolor='dimgray', elinewidth=1, capsize=2, markersize=4)
    plt.legend(loc='upper left', bbox_to_anchor=(1,1))
    plt.text(0.99, 1.10, f'N = {len(df)}', transform=plt.gca().transAxes, fontsize=14, verticalalignment='top', horizontalalignment='right')
    plt.xlabel(xAxis)
    plt.ylabel(yAxis)
    plt.title(f'{xAxis} vs {yAxis}')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/png/scatter_{output_title}.png')
    plt.savefig(f'{output_dir}/svg/scatter_{output_title}.svg')
    # add a line of best fit and an r^2 value
    m, b = np.polyfit(df[xAxis], df[yAxis], regression_degree)
    plt.plot(df[xAxis], m*df[xAxis] + b, color='red')
    # add the r^2 value to the top left of the plot
    r2 = np.corrcoef(df[xAxis], df[yAxis])[0,1]**2
    plt.text(0.01, 1.10, f'r^2 = {r2:.2f}', transform=plt.gca().transAxes, fontsize=14, verticalalignment='top')
    plt.savefig(f'{output_dir}/png/scatterRegression_{output_title}_{regression_degree}.png')
    plt.savefig(f'{output_dir}/svg/scatterRegression_{output_title}_{regression_degree}.svg')
    plt.clf()

def plotScatterplotSingle(df, sample, xAxis, yAxis, yStd, regression_degree, output_title, output_dir, sampleType=0, color=0):
    df_sample = df[df['Sample'] == sample]
    # plot the WT sequence fluorescence vs the energy
    plt.scatter(df_sample[xAxis], df_sample[yAxis], color=colors[i], label=sample, s=5)
    # plot the standard deviation
    plt.errorbar(df_sample[xAxis], df_sample[yAxis], yerr=df_sample[yStd], fmt='o', color=colors[i], ecolor='dimgray', elinewidth=1, capsize=2, markersize=4)
    plt.text(0.99, 1.10, f'N = {len(df)}', transform=plt.gca().transAxes, fontsize=14, verticalalignment='top', horizontalalignment='right')
    plt.xlabel(xAxis)
    plt.ylabel(yAxis)
    # set the y axis limits
    plt.ylim(0, 1.75)
    # set the x axis limits
    plt.xlim(-60, 0)
    plt.title(f'{xAxis} vs {yAxis}')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/png/scatter_{output_title}.png')
    plt.savefig(f'{output_dir}/svg/scatter_{output_title}.svg')
    # add a line of best fit and an r^2 value
    m, b = np.polyfit(df_sample[xAxis], df_sample[yAxis], regression_degree)
    plt.plot(df_sample[xAxis], m*df_sample[xAxis] + b, color='red')
    # add the r^2 value to the top left of the plot
    r2 = np.corrcoef(df_sample[xAxis], df_sample[yAxis])[0,1]**2
    plt.text(0.01, 1.10, f'r^2 = {r2:.2f}', transform=plt.gca().transAxes, fontsize=14, verticalalignment='top')
    plt.savefig(f'{output_dir}/png/scatterRegression_{output_title}.png')
    plt.savefig(f'{output_dir}/svg/scatterRegression_{output_title}.svg')
    plt.clf()

def addEnergyDifferencesToDataframe(df, cols):
    for col in cols:
        #df[f'{col}Diff'] = df[f'{col}DimerPreOptimize'] - df[f'{col}Monomer']
        df[f'{col}Diff'] = df[f'{col}DimerOptimize'] - df[f'{col}Monomer']
    return df

if __name__ == '__main__':
    # read in the data file
    dataFile = sys.argv[1]
    df = pd.read_csv(dataFile)

    # get the output directory
    outputDir = sys.argv[2]

    #xAxis = 'TotalPreOptimize'
    xAxis = 'Total'
    yAxis = 'PercentGpA'

    # make the output directory if it doesn't exist and the png and svg subdirectories
    os.makedirs(outputDir, exist_ok=True)
    os.makedirs(f'{outputDir}/png', exist_ok=True)
    os.makedirs(f'{outputDir}/svg', exist_ok=True)

    # only keep sequences with the lowest total energy
    df = df.sort_values(by=[xAxis], ascending=True)
    df = df.drop_duplicates(subset=['Sequence'], keep='first')
    # move the sequence column to the front of the dataframe
    cols = df.columns.tolist()
    cols.insert(0, cols.pop(cols.index('Sequence')))

    # TRIMMING THE DATAFRAME
    df = df[df['PercentGpA'] < 2]
    df = df[df['PercentGpA'] - df['PercentStd'] > 0]
    df = df[df['PercentStd'] < .15]
    df = df[df['Sample'].notnull()]
    df = df[df['PercentGpA'] > 0]

    # add energy differences to the dataframe
    cols = ['VDW', 'HBOND', 'IMM1']
    df = addEnergyDifferencesToDataframe(df, cols)
    df.to_csv(f'{outputDir}/lowestEnergySequences.csv', index=False)

    # only plot the sequences with the HBONDDiff > 5
    lowHbond_df = df[df['HBONDDiff'] > -5]
    lowHbond_df = lowHbond_df[lowHbond_df[xAxis] < 0]
    # save the lowHbond_df to a csv file
    lowHbond_df.to_csv(f'{outputDir}/lowHbond_df.csv', index=False)
    df = df[df[xAxis] < 0]

    # save the df to a csv file
    df.to_csv(f'{outputDir}/plotData.csv', index=False)

    # make list of dfs to plot
    df_list = [df, lowHbond_df]
    outputTitle_list = ['TotalEnergy', 'LowHbond']

    for df_tmp,title in zip(df_list, outputTitle_list):
        plotScatterplot(df_tmp, xAxis, yAxis, 'PercentStd', 1, title, outputDir)

    for sample in df['Sample'].unique():
        df_sample = df[df['Sample'] == sample]
        # check that the df_sample is not empty
        if df_sample.empty:
            continue
        plotScatterplot(df_sample, xAxis, yAxis, 'PercentStd', 1, f'{sample}_Total', outputDir)

    for sample, i in zip(df['Sample'].unique(), range(len(df['Sample'].unique()))):
        plotScatterplotSingle(df, sample, xAxis, yAxis, 'PercentStd', 1, f'{sample}_Total', outputDir, sampleType=sample, color=colors[i])