'''
File: /home/loiseau@ad.wisc.edu/github/Sequence-Design/ngsReconstruction/CHIP2/fluorescenceAnalysis/code/adjustFluorByControlFlow_percentGpA.py
Project: /home/loiseau@ad.wisc.edu/github/Sequence-Design/ngsReconstruction/CHIP2/fluorescenceAnalysis/code
Created Date: Monday August 28th 2023
Author: loiseau
-----
Last Modified: Monday August 28th 2023 10:09:06 am
Modified By: loiseau
-----
Description: 
This script takes the following inputs:
    - reconstructed fluorescence dataframe
    - flow fluorescence dataframe of controls
    - output directory
For every replicate, it adjusts the fluorescence of the reconstruction by the fluorescence of the flow controls.
-----
'''

import sys, os, pandas as pd, numpy as np, matplotlib.pyplot as plt, argparse
from scipy import stats

# initialize the parser
parser = argparse.ArgumentParser(description='Adjust the reconstructed fluorescence by the flow fluorescence of the controls')

# add the necessary arguments
parser.add_argument('-recFile','--reconstructionFile', type=str, help='the input reconstructed fluorescence csv file')
parser.add_argument('-flowFile','--controlFlowFile', type=str, help='the input flow fluorescence csv file')
# add the optional arguments
parser.add_argument('-outDir','--outputDir', type=str, help='the output directory')

# extract the arguments into variables
args = parser.parse_args()
reconstructionFile = args.reconstructionFile
controlFlowFile = args.controlFlowFile
# default values for the optional arguments
outputDir = os.getcwd()
# if the optional arguments are not specified, use the default values
if args.outputDir is not None:
    outputDir = args.outputDir
    os.makedirs(outputDir, exist_ok=True)

def plot_and_transform(df_control_plot, input_df, xaxis, cols, sample, outputColName, x_stdCol, y_stdCol, outputDir):
    output_df = input_df.copy()
    df_control_plot[y_stdCol] = df_control_plot[cols].std(axis=1)
    for col in cols:
        print(col)
        # get the standard deviation of the rep columns
        label = f'{sample}_{col}'
        print(label)
        print(xaxis)
        print(col)
        slope, yint = plot_and_get_regression(df_control_plot, xaxis, col, x_stdCol, y_stdCol, label, outputDir)
        transform_col = f'{col}_{outputColName}' 
        tmp_col = ((df_sample[col] - yint) / slope)
        # add col to a new column in the reconstruction dataframe
        output_df[transform_col] = tmp_col
    return output_df

def plot_and_get_regression(df_control_plot, xaxis_col, yaxis_col, x_stdCol, y_stdCol, sample, outputDir):
    xaxis = df_control_plot[xaxis_col]
    yaxis = df_control_plot[yaxis_col]
    plt.scatter(xaxis, yaxis)
    # plot the line of best fit
    m, b = np.polyfit(xaxis, yaxis, 1)
    plt.plot(xaxis, m*xaxis + b)
    
    # plot the standard deviation for each point
    std_x = df_control_plot[x_stdCol]
    std_y = df_control_plot[y_stdCol]
    #std_x = df_control_plot['Percent GpA stdev']
    #std_y = df_control_plot['std']
    plt.errorbar(xaxis, yaxis, yerr=std_y, xerr=std_x, fmt='none', ecolor='black')
    plt.xlabel(xaxis_col)
    #plt.ylabel(yaxis_col)
    plt.ylabel('Reconstructed Fluorescence')
    plt.title(sample)
    # add the equation to the plot
    plt.text(0.05, 0.95, f'y = {m:.2f}x + {b:.2f}', transform=plt.gca().transAxes)
    # add the r^2 value to the plot
    plt.text(0.05, 0.90, f'r^2 = {np.corrcoef(xaxis, yaxis)[0,1]**2:.2f}', transform=plt.gca().transAxes)
    plt.savefig(f'{outputDir}/{sample}_{xaxis_col}_fit.png')
    plt.savefig(f'{outputDir}/{sample}_{xaxis_col}_fit.svg')
    plt.clf()
    return m, b

def calculate_mean_and_std(input_df, columns, meanColName, stdColName):
    output_df = input_df.copy()
    output_df[meanColName] = output_df[columns].mean(axis=1)
    output_df[stdColName] = output_df[columns].std(axis=1)
    return output_df

def calculateUncertainty(input_df, gpa_error, transform_col, gpaFluor):
    output_df = input_df.copy()
    output_df['Uncertainty'] = output_df['Percent Error'] + gpa_error 
    output_df['std_adjusted'] = output_df['Uncertainty'] * output_df[transform_col]
    return output_df 

# get the err of the slope and intercept
# https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.linregress.html
def get_regression_stats(xaxis, yaxis):
    result = stats.linregress(xaxis, yaxis)
    slope, intercept, r_value, p_value, slope_err, intercept_err = result.slope, result.intercept, result.rvalue, result.pvalue, result.stderr, result.intercept_stderr
    return slope_err, intercept_err

if __name__ == '__main__':
    gpa = 'LIIFGVMAGVIGT'
    g83i = 'LIIFGVMAIVIGT'
    
    #percentGpaCol = 'Percent GpA'
    #fluorCol = 'Flow Mean'
    #yaxis = 'Mean Std'
    percentGpaCol = 'PercentGpA'
    percentGpaStd_col = 'PercentStd'
    toxgreenCol = 'Fluorescence'
    toxgreenStd_col = 'FluorStd'
    initial_transform_col = 'reconstruction_transformed'
    final_transform_col = 'PercentGpA_transformed'
    
    # read in the dataframes
    reconstruction_df = pd.read_csv(reconstructionFile)
    controlFlow_df = pd.read_csv(controlFlowFile)

    # divide the percent GpA by 100 to get the fraction
    controlFlow_df[percentGpaCol] = controlFlow_df[percentGpaCol]/100
    controlFlow_df[percentGpaStd_col] = controlFlow_df[percentGpaStd_col]/100
    
    # make directories for outputs
    correlationDir = f'{outputDir}/correlation_plots'
    dataDir = f'{outputDir}/correlation_data'
    os.makedirs(correlationDir, exist_ok=True)
    os.makedirs(dataDir, exist_ok=True)
    
    # get the sample names (different flow runs for each design. If you don't have multiple flow runs, this should still work as long as you have a sample column for your data)
    sample_names = reconstruction_df['Sample'].unique()
    output_df = pd.DataFrame()
    # loop through each sample
    for sample in sample_names:
        # get the reconstruction data for this sample
        df_sample = reconstruction_df[reconstruction_df['Sample'] == sample]

        # get the matching sequences from the control flow dataframe (includes controls and can include any sequences you've run in TOXGREEN individually if it is also in your CHIP)
        df_sample_controls = df_sample[df_sample['Sequence'].isin(controlFlow_df['Sequence'])]
        df_control_plot = controlFlow_df.copy()
        #print(df_control_plot)

        # get the columns that contain Rep (the columns with the fluorescence data)
        df_control_plot = df_control_plot.merge(df_sample_controls[['Sequence', 'Rep1-Fluor', 'Rep2-Fluor', 'Rep3-Fluor', 'Sample']], on='Sequence')
        #cols = [col for col in df_control_plot.columns if 'Rep' in col]
        cols = [col for col in df_sample.columns if 'Rep' in col]

        # remove any rows with 0 fluorescence and output the control plot data
        df_control_plot = df_control_plot[(df_control_plot[cols] != 0).all(axis=1)]
        df_sample = df_sample[(df_sample[cols] != 0).all(axis=1)]
        df_control_plot.to_csv(f'{dataDir}/{sample}_controlFlow.csv', index=False)

        # transform the data to toxgreen percent GpA (creates a trendline between reconstructed fluorescence and toxgreen fluorescence and uses correlation equation to transform data)
        df_sample = plot_and_transform(df_control_plot, df_sample, percentGpaCol, cols, sample, 'transformed', percentGpaStd_col, 'std', correlationDir)
        percentGpa_cols = [col for col in df_sample.columns if 'transformed' in col]
        df_sample = calculate_mean_and_std(df_sample, percentGpa_cols, initial_transform_col, 'std_adjusted')

        # check if toxgreenCol is in the columns 
        if toxgreenCol in df_control_plot.columns:
            # transform the data to toxgreen fluorescence (to also do the same thing but with raw fluorescence values rather than percent GpA values)
            df_sample = plot_and_transform(df_control_plot, df_sample, toxgreenCol, cols, sample, 'toxgreen', toxgreenStd_col, 'std', correlationDir)
            toxgreen_cols = [col for col in df_sample.columns if 'toxgreen' in col]
            df_sample = calculate_mean_and_std(df_sample, toxgreen_cols, 'toxgreen_fluor', 'toxgreen_std')

        # get the index of GpA and G83I from the sequence column and get the fluorescence from the index
        gpaIndex, g83iIndex = df_sample[df_sample['Sequence'] == gpa], df_sample[df_sample['Sequence'] == g83i]
        gpaFluor, g83iFluor = gpaIndex[initial_transform_col].values[0], g83iIndex[initial_transform_col].values[0]

        # define the adjusted fluorescence
        df_sample[final_transform_col] = df_sample[initial_transform_col]/gpaFluor
        df_sample['PercentGpA_reconstructed_GpA'] = df_sample[final_transform_col]/gpaFluor*100 

        # keeping for posterity; the older way I was trying to calculate uncertainty that never worked properly
        #gpa_sd = controlFlow_df[controlFlow_df['Sequence'] == gpa][percentGpaStd_col].values[0]
        #gpa_error = gpa_sd/gpaFluor
        ##df_sample = calculateUncertainty(df_sample, gpa_error, transform_col, gpaFluor)

        # save the transformed data to a csv
        df_sample.to_csv(f'{dataDir}/{sample}_transformed.csv', index=False)
        #df_sample = df_sample[df_sample[final_transform_col] > 0]

        # keep sequences with a higher fluorescence than G83I and save to a csv
        df_sample_g83i = df_sample[df_sample[final_transform_col] > g83iFluor]
        df_sample_g83i.to_csv(f'{dataDir}/{sample}_transformed_greater_than_G83I.csv', index=False)

        # add the sample to the output dataframe
        output_df = pd.concat([output_df, df_sample])

    output_df.to_csv(f'{outputDir}/all_transformed.csv', index=False)
    