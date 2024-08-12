import os, sys, pandas as pd, argparse
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from scipy import stats

"""
    Plots CATM vs repack RMSD data
"""

# initialize the parser
parser = argparse.ArgumentParser(description='Compiles energyFile.csv files from an input directory')

# add the necessary arguments
parser.add_argument('-inFile','--inputFile', type=str, help='the input directory')
parser.add_argument('-outDir','--outputDir', type=str, help='the output directory')

# extract the arguments into variables
args = parser.parse_args()
inputFile = args.inputFile
# default values for the optional arguments
outputDir = os.getcwd()
# if the optional arguments are not specified, use the default values
if args.outputDir is not None:
    outputDir = args.outputDir
    os.makedirs(outputDir, exist_ok=True)

# Functions
def plotScatterplot(input_df, label, xAxis, yAxis, text_font_size, regression_degree, output_dir):
    # make a scatter plot of the data
    plt.scatter(input_df[xAxis], input_df[yAxis])
    # get the spearman rank order correlation
    spearman_corr, spearman_p = stats.spearmanr(input_df[xAxis], input_df[yAxis])
    # add the spearman correlation to the plot
    plt.text(0.01, 1.00, f'Spearman r = {spearman_corr:.2f}', transform=plt.gca().transAxes, fontsize=text_font_size, verticalalignment='top')
    # add the spearman p-value to the plot
    plt.text(0.01, 0.90, f'Spearman p = {spearman_p}', transform=plt.gca().transAxes, fontsize=text_font_size, verticalalignment='top')
    # add a line of best fit and an r^2 value
    try:
        m, b = np.polyfit(input_df[xAxis], input_df[yAxis], regression_degree)
    except:
        print(f'Error in calculating the regression for {xAxis} vs {yAxis}; "SVD did not converge in Linear Least Squares"')
        plt.close()
        plt.clf()
        exit(0)
    plt.plot(input_df[xAxis], m*input_df[xAxis] + b, color='red')
    # add the r^2 value to the top left of the plot
    r2 = np.corrcoef(input_df[xAxis], input_df[yAxis])[0,1]**2
    plt.text(0.01, 1.2, f'r^2 = {r2:.3f}', transform=plt.gca().transAxes, fontsize=text_font_size, verticalalignment='top')
    # add the regression equation to the top left of the plot
    plt.text(0.01, 1.15, f'y = {m:.3f}x + {b:.3f}', transform=plt.gca().transAxes, fontsize=text_font_size, verticalalignment='top')
    plt.xlabel(xAxis)
    plt.ylabel(yAxis)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/{label}_rmsd_{xAxis}_vs_{yAxis}.png')
    plt.savefig(f'{output_dir}/{label}_rmsd_{xAxis}_vs_{yAxis}.svg')
    plt.close()
    input_df.to_csv(f'{output_dir}/{label}_rmsd.csv')

if __name__ == '__main__':
    # define the output dataframe
    outputDf = pd.DataFrame()
    # read the input file
    inputDf = pd.read_csv(inputFile)

    # analyze the rmsd output
    low_rmsd = inputDf[inputDf['RMSD'] < 1]
    mid_rmsd = inputDf[(inputDf['RMSD'] >= 1) & (inputDf['RMSD'] < 2)]
    high_rmsd = inputDf[inputDf['RMSD'] >= 2]
    # put the rmsd values into a list
    rmsds = [low_rmsd, mid_rmsd, high_rmsd]
    rmsd_labels = ['Low', 'Mid', 'High']

    # print statements
    print(f'Low RMSD: {len(low_rmsd)}')
    print(f'Mid RMSD: {len(mid_rmsd)}')
    print(f'High RMSD: {len(high_rmsd)}')
    print(f'Mean RMSD: {np.mean(inputDf["RMSD"])}')
    print(f'Median RMSD: {np.median(inputDf["RMSD"])}')
    print(f'Std RMSD: {np.std(inputDf["RMSD"])}')
    print(f'Min RMSD: {np.min(inputDf["RMSD"])}')
    print(f'Max RMSD: {np.max(inputDf["RMSD"])}')

    # plot energy vs percentGpA for each group
    xAxis = 'Total'
    yAxis = 'PercentGpA'
    text_font_size = 10
    regression_degree = 1
    for rmsd_df, label in zip(rmsds, rmsd_labels):
        plotScatterplot(rmsd_df, label, xAxis, yAxis, text_font_size, regression_degree, outputDir)
        plotScatterplot(rmsd_df, label, 'Repack_Total', yAxis, text_font_size, regression_degree, outputDir)
        plotScatterplot(rmsd_df, label, 'Repack_Total', 'Total', text_font_size, regression_degree, outputDir)

    ## get the averages for different groups (similar to Samantha's data)
    #low = inputDf[(inputDf['PercentGpA'] >= .25) & (inputDf['PercentGpA'] < .5)]
    #medium = inputDf[(inputDf['PercentGpA'] >= .5) & (inputDf['PercentGpA'] < .75)]
    #high = inputDf[(inputDf['PercentGpA'] >= .75) & (inputDf['PercentGpA'] < 1)]
    #aboveGpA = inputDf[inputDf['PercentGpA'] >= 1]
    ## get the averages for each group
    #lowAvg = low.mean()
    #mediumAvg = medium.mean()
    #highAvg = high.mean()
    #aboveGpAAvg = aboveGpA.mean()
    ## add the number of sequences to each group
    #lowAvg['numSequences'] = len(low)
    #mediumAvg['numSequences'] = len(medium)
    #highAvg['numSequences'] = len(high)
    #aboveGpAAvg['numSequences'] = len(aboveGpA)
    ## save the averages to a csv file
    #avgDf = pd.concat([lowAvg, mediumAvg, highAvg, aboveGpAAvg], axis=1)
    #avgDf.columns = ['Low', 'Medium', 'High', 'AboveGpA']
    ## get the standard deviations for each group
    #lowStd = low.std()
    #mediumStd = medium.std()
    #highStd = high.std()
    #aboveGpAStd = aboveGpA.std()
    ## add the standard deviations to the dataframe
    #stdDf = pd.concat([lowStd, mediumStd, highStd, aboveGpAStd], axis=1)
    #stdDf.columns = ['LowStd', 'MediumStd', 'HighStd', 'AboveGpAStd']
    ## add the standard deviations to the averages dataframe
    #avgDf = pd.concat([avgDf, stdDf], axis=1)
    ## change the column order
    #avgDf = avgDf[['Low', 'LowStd', 'Medium', 'MediumStd', 'High', 'HighStd', 'AboveGpA', 'AboveGpAStd']]
    #avgDf.to_csv(f'{outputDir}/averages.csv')

    ## define the x and y axes
    #xAxis = 'energy'
    #yAxis = 'PercentGpA'
    #text_font_size = 10
    #regression_degree = 1
    ## make a scatter plot of the data
    #plt.scatter(inputDf[xAxis], inputDf[yAxis])
    ## get the spearman rank order correlation
    #spearman_corr, spearman_p = stats.spearmanr(inputDf[xAxis], inputDf[yAxis])
    ## add the spearman correlation to the plot
    #plt.text(0.01, 1.00, f'Spearman r = {spearman_corr:.2f}', transform=plt.gca().transAxes, fontsize=text_font_size, verticalalignment='top')
    ## add the spearman p-value to the plot
    #plt.text(0.01, 0.90, f'Spearman p = {spearman_p}', transform=plt.gca().transAxes, fontsize=text_font_size, verticalalignment='top')
    ## add a line of best fit and an r^2 value
    #try:
    #    m, b = np.polyfit(inputDf[xAxis], inputDf[yAxis], regression_degree)
    #except:
    #    print(f'Error in calculating the regression for {xAxis} vs {yAxis}; "SVD did not converge in Linear Least Squares"')
    #    plt.close()
    #    plt.clf()
    #    exit(0)
    #plt.plot(inputDf[xAxis], m*inputDf[xAxis] + b, color='red')
    ## add the r^2 value to the top left of the plot
    #r2 = np.corrcoef(inputDf[xAxis], inputDf[yAxis])[0,1]**2
    #plt.text(0.01, 1.2, f'r^2 = {r2:.3f}', transform=plt.gca().transAxes, fontsize=text_font_size, verticalalignment='top')
    ## add the regression equation to the top left of the plot
    #plt.text(0.01, 1.15, f'y = {m:.3f}x + {b:.3f}', transform=plt.gca().transAxes, fontsize=text_font_size, verticalalignment='top')
    #plt.xlabel('Energy Score (kcal/mol)')
    #plt.ylabel('Percent GpA')
    #plt.tight_layout()
    #plt.savefig(f'{outputDir}/energy_vs_percentGpA.png')
    #plt.savefig(f'{outputDir}/energy_vs_percentGpA.svg')
    