import os, sys, pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np

colors = ['mediumseagreen', 'navajowhite', 'darkslateblue', 'brown', 'pink', 'gray', 'olive', 'cyan']
# plot scatterplot function
#TODO: could get a standard deviation for the x axis energies now that I have multiple repack energies
def plotScatterplot(df, xAxis, yAxis, yStd, regression_degree, output_title, output_dir, addColors):
    if addColors:
        for sample, i in zip(df['Sample'].unique(), range(len(df['Sample'].unique()))):
            df_sample = df[df['Sample'] == sample]
            # plot the WT sequence fluorescence vs the energy
            plt.scatter(df_sample[xAxis], df_sample[yAxis], color=colors[i], label=sample, s=5)
            # plot the standard deviation
            plt.errorbar(df_sample[xAxis], df_sample[yAxis], yerr=df_sample[yStd], fmt='o', color=colors[i], ecolor='lightgray', elinewidth=3, capsize=0, markersize=5)
        plt.legend(loc='upper left', bbox_to_anchor=(1,1))
    else:
        # make a scatter plot of the total energy vs the percent gpa
        plt.scatter(df[xAxis], df[yAxis], s=3)
        plt.errorbar(df[xAxis], df[yAxis], yerr=df[yStd], fmt='o', ecolor='lightgray', elinewidth=3, capsize=0, markersize=3)
    plt.xlabel(xAxis)
    plt.ylabel(yAxis)

    # set the yAxis lower limit to 0
    #plt.ylim(bottom=0)
    #plt.ylim(top=160)
    # set size of the points
    # add in the standard deviation
    plt.title(f'{xAxis} vs {yAxis}')
    #plt.errorbar(df[xAxis], df[yAxis], yerr=df[yStd], fmt='none', ecolor='black')
    plt.text(0.99, 1.10, f'N = {len(df)}', transform=plt.gca().transAxes, fontsize=14, verticalalignment='top', horizontalalignment='right')
    plt.savefig(f'{output_dir}/scatter_{output_title}.png')

    # add a line of best fit and an r^2 value
    m, b = np.polyfit(df[xAxis], df[yAxis], regression_degree)
    plt.plot(df[xAxis], m*df[xAxis] + b, color='red')
    # TODO: try the below code for sklearn regressions
    #    model = np.polyfit(df[xAxis], df[yAxis], regression_degree)
    #    predict = np.poly1d(model)
    #    x_lin_reg = np.linspace(df[xAxis].min(), df[xAxis].max(), 100)
    #    plt.plot(x_lin_reg, predict(x_lin_reg), color='red')

    # add the r^2 value to the top left of the plot
    r2 = np.corrcoef(df[xAxis], df[yAxis])[0,1]**2
    plt.text(0.01, 1.10, f'r^2 = {r2:.2f}', transform=plt.gca().transAxes, fontsize=14, verticalalignment='top')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/scatterRegression_{output_title}_{regression_degree}.png')
    plt.clf()

def addEnergyDifferencesToDataframe(df, cols):
    for col in cols:
        df[f'{col}Diff'] = df[f'{col}DimerOptimize'] - df[f'{col}Monomer']
    return df

if __name__ == '__main__':
    # read in the data file
    dataFile = sys.argv[1]
    df = pd.read_csv(dataFile)

    # get the output directory
    outputDir = sys.argv[2]
    percentStdCutoff = 15

    # only keep sequences with the lowest total energy
    df = df.sort_values(by=['Total'], ascending=True)
    df = df.drop_duplicates(subset=['Sequence'], keep='first')
    # move the sequence column to the front of the dataframe
    cols = df.columns.tolist()
    cols.insert(0, cols.pop(cols.index('Sequence')))

    # rid of any sequences where the PercentStd > 10
    df = df[df['PercentStd'] < percentStdCutoff]
    df = df[df['PercentGpA'] < 3]
    df = df[df['Total'] < 0]

    # TESTS
    #df = df[df['PercentGpA'] > 0.50]
    #maltose_col = 'LB-12H_M9-36H'
    #maltose_cutoff = -99.9
    #maltose_limit = 99999900 
    #df = df[df[maltose_col] > maltose_cutoff]
    #df = df[df[maltose_col] < maltose_limit]

    # add energy differences to the dataframe
    cols = ['VDW', 'HBOND', 'IMM1']
    df = addEnergyDifferencesToDataframe(df, cols)
    df.to_csv(f'{outputDir}/lowestEnergySequences.csv', index=False)

    # only plot the sequences with the HBONDDiff > 5
    lowHbond_df = df[df['HBONDDiff'] > -5]
    # save the lowHbond_df to a csv file
    lowHbond_df.to_csv(f'{outputDir}/lowHbond_df.csv', index=False)

    # make list of dfs to plot
    df_list = [df, lowHbond_df]
    outputTitle_list = ['TotalEnergy', 'LowHbond']

    for df_tmp,title in zip(df_list, outputTitle_list):
        plotScatterplot(df_tmp, 'Total', 'PercentGpA', 'PercentStd', 1, title, outputDir, True)

    for sample in df['Sample'].unique():
        df_sample = df[df['Sample'] == sample]
        #for degree in [1,5]:
        #    print(degree)
        #    exit(0)
        plotScatterplot(df_sample, 'Total', 'PercentGpA', 'PercentStd', 1, f'{sample}_Total', outputDir, False)

    #TODO: write a script that will take in the energy file, combine it with the clashing file, and then use this script to plot the data