'''
File: d:\github\Sequence-Design\ngsReconstruction\CHIP2_analysisCode\adjustFluorByControlFlow.py
Project: d:\github\Sequence-Design\ngsReconstruction\CHIP2_analysisCode
Created Date: Friday August 11th 2023
Author: gjowl
-----
Last Modified: Friday August 11th 2023 2:40:16 pm
Modified By: gjowl
-----
Description:  
This script takes the following inputs:
    - reconstructed fluorescence dataframe
    - flow fluorescence dataframe of controls
    - output directory
For every replicate, it adjusts the fluorescence of the reconstruction by the fluorescence of the flow controls.
-----
'''

import sys, os, pandas as pd, numpy as np, matplotlib.pyplot as plt

def plot_and_transform(df_control_plot, df_sample, xaxis, cols, sample, outputDir):
    output_df = df_sample.copy()
    for col in cols:
        yaxis = df_control_plot[col]
        plt.scatter(xaxis, yaxis)
        # plot the line of best fit
        m, b = np.polyfit(xaxis, yaxis, 1)
        plt.plot(xaxis, m*xaxis + b)
        plt.xlabel('Flow Mean')
        plt.ylabel(col)
        plt.title(sample)
        # add the equation to the plot
        plt.text(0.05, 0.95, f'y = {m:.2f}x + {b:.2f}', transform=plt.gca().transAxes)
        # add the r^2 value to the plot
        plt.text(0.05, 0.90, f'r^2 = {np.corrcoef(xaxis, yaxis)[0,1]**2:.2f}', transform=plt.gca().transAxes)
        plt.savefig(f'{outputDir}/{sample}_{col}_fit.png')
        plt.clf()
        # transform the reconstruction data
        tmp_col = ((output_df[col] - b) / m)
        # add col to a new column in the reconstruction dataframe
        output_df[f'{col}_transformed'] = tmp_col
    # get the mean of the transformed data
    output_df['Fluor_transformed'] = output_df[[f'{col}_transformed' for col in cols]].mean(axis=1)

def plot_and_get_regression(df_control_plot, xaxis_col, yaxis_col, sample):
    xaxis = df_control_plot[xaxis_col]
    yaxis = df_control_plot[yaxis_col]
    plt.scatter(xaxis, yaxis)
    # plot the line of best fit
    m, b = np.polyfit(xaxis, yaxis, 1)
    plt.plot(xaxis, m*xaxis + b)
    # plot the standard deviation for each point
    std_x = df_control_plot['Mean Std']
    std_y = df_control_plot['std']
    #std_x = df_control_plot['Percent GpA stdev']
    #std_y = df_control_plot['std']
    plt.errorbar(xaxis, yaxis, yerr=std_y, xerr=std_x, fmt='none', ecolor='black')
    plt.xlabel(xaxis_col)
    plt.ylabel(yaxis_col)
    plt.title(sample)
    # add the equation to the plot
    plt.text(0.05, 0.95, f'y = {m:.2f}x + {b:.2f}', transform=plt.gca().transAxes)
    # add the r^2 value to the plot
    plt.text(0.05, 0.90, f'r^2 = {np.corrcoef(xaxis, yaxis)[0,1]**2:.2f}', transform=plt.gca().transAxes)
    plt.savefig(f'{outputDir}/{sample}_fit.png')
    plt.clf()
    return m, b

def transform_col(df_sample, sample, slope, y_intercept, col, output_df):
    output_df = df_sample.copy()
    # transform the reconstruction data
    tmp_col = ((output_df[col] - y_intercept) / slope)
    # add col to a new column in the reconstruction dataframe
    output_df[f'{col}_transformed'] = tmp_col
    return output_df
    
def calculateStandardDeviation(df_sample, cols, sample):
    output_df = df_sample.copy()
    output_df['std'] = df_sample[cols].std(axis=1)
    mean = output_df[cols].mean(axis=1)
    output_df['Percent Error'] = output_df['std']/mean*100
    return output_df

# read in the reconstructed fluorescence dataframe
reconstructionFile = sys.argv[1]
controlFlowFile = sys.argv[2]
outputDir = sys.argv[3]

gpa = 'LIIFGVMAGVIGT'
g83i = 'LIIFGVMAIVIGT'
#noTM_fluor = 17870
#flow_noTM_fluor = 28563
# noTM from flow reruns
noTM_fluor = 12429.6644
subtract_noTM = False 
#subtract_noTM = False 
#TODO: the subtraction of the noTM fluor works, but it leads to some negative values. Maybe I should just add it to the fitting line as a control fluor?

os.makedirs(outputDir, exist_ok=True)

xaxis = 'Flow Mean'
yaxis = 'mean'
#xaxis = 'Percent GpA'
#yaxis = 'mean_transformed'

# read in the dataframes
reconstruction_df = pd.read_csv(reconstructionFile)
controlFlow_df = pd.read_csv(controlFlowFile)

# get the sample names
sample_names = reconstruction_df['Sample'].unique()

# loop through each sample
output_df = pd.DataFrame()
for sample in sample_names:
    # get the reconstruction data for this sample
    df_sample = reconstruction_df[reconstruction_df['Sample'] == sample]
    # get the matching sequence from the control flow dataframe
    df_sample_controls = df_sample[df_sample['Sequence'].isin(controlFlow_df['Sequence'])]
    df_control_plot = controlFlow_df.copy()
    # get the columns that contain rep
    df_control_plot = df_control_plot.merge(df_sample_controls[['Sequence', 'Rep1-Fluor', 'Rep2-Fluor', 'Rep3-Fluor', 'Sample']], on='Sequence')
    # get the columns that contain rep
    cols = [col for col in df_control_plot.columns if 'Rep' in col]
    if sample == 'G' or sample == 'R':
        cols = [col for col in cols if 'Rep1' not in col]
    # only keep the rows where no value is not 0
    df_control_plot = df_control_plot[(df_control_plot[cols] != 0).all(axis=1)]
    df_sample = df_sample[(df_sample[cols] != 0).all(axis=1)]
    if subtract_noTM:
        #df_control_plot[cols] = df_control_plot[cols] - flow_noTM_fluor
        df_control_plot[cols] = df_control_plot[cols] - noTM_fluor
        df_sample[cols] = df_sample[cols] - noTM_fluor
    # get the standard deviation of the rep columns
    df_sample = calculateStandardDeviation(df_sample, cols, sample)
    # get the mean of the rep columns
    df_control_plot['mean'] = df_control_plot[cols].mean(axis=1)
    # add the standard deviation of the mean to the dataframe
    df_control_plot['std'] = df_control_plot[cols].std(axis=1)
    df_sample['mean'] = df_sample[cols].mean(axis=1)
    slope, yint = plot_and_get_regression(df_control_plot, xaxis, yaxis, sample)
    # transform the reconstruction data 
    df_sample = transform_col(df_sample, sample, slope, yint, 'mean', output_df)
    # get the index of GpA and G83I from the sequence column 
    gpaIndex, g83iIndex = df_sample[df_sample['Sequence'] == gpa], df_sample[df_sample['Sequence'] == g83i]
    # get the fluorescence from the index
    fluor_transform_col = f'mean_transformed'
    gpaFluor, g83iFluor = gpaIndex[fluor_transform_col].values[0], g83iIndex[fluor_transform_col].values[0]
    df_sample['Percent GpA'] = df_sample[fluor_transform_col]/gpaFluor*100 
    # save the transformed data
    df_sample.to_csv(f'{outputDir}/{sample}_transformed.csv', index=False)
    df_sample = df_sample[df_sample['mean_transformed'] > 0]
    # keep sequences with a higher fluorescence than G83I
    df_sample_g83i = df_sample[df_sample[fluor_transform_col] > g83iFluor]
    # save the filtered data
    df_sample_g83i.to_csv(f'{outputDir}/{sample}_g83i_filtered.csv', index=False)
    # add the sample to the output dataframe
    output_df = pd.concat([output_df, df_sample])
    # add in a way to add a standard error? Should I try to calculate standard error for each sequence by using the count of sequences from the flow data? Would that give my values more weight?
    # I think I can at the very least transform the standard deviation and then do percent GpA of that error?
    # I think the standard error formula is standard deviation / sqrt(n)
    # TODO: get G to I mutants for GASrights and evaluate those sequence
output_df.to_csv(f'{outputDir}/all_transformed.csv', index=False)
