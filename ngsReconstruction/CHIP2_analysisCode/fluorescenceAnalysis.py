'''
File: d:\github\Sequence-Design\ngsReconstruction\CHIP2_analysisCode\fluorescenceAnalysis.py
Project: d:\github\Sequence-Design\ngsReconstruction\CHIP2_analysisCode
Created Date: Saturday August 5th 2023
Author: gjowl
-----
Last Modified: Saturday August 5th 2023 4:10:06 pm
Modified By: gjowl
-----
Description: ...add description here... 
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------
'''

import sys, os, pandas as pd, numpy as np, matplotlib.pyplot as plt

# global variable

def calculateMeanFluorescence(df_fluor):
    input_df = df_fluor.copy()
    output_df = df_fluor.copy()
    # keep only the columns that contain Rep
    input_df = input_df[input_df.columns[input_df.columns.str.contains('Rep')]]
    mean = input_df.mean(axis=1)
    std = input_df.std(axis=1)
    output_df['mean'] = mean
    output_df['std'] = std
    input_df['product'] = input_df[input_df.columns].prod(axis=1)
    df_zeros = input_df[input_df['product'] == 0]
    # keep only the indices from input_df in output_df
    output_df = output_df.drop(df_zeros.index)
    return output_df 

def getColors(labels):
    # get colors for the pie chart
    colors = []
    for label in labels:
        if label == 'Protein < G83I':
            colors.append('red')
        elif label == 'Protein > GpA':
            colors.append('yellow')
        else:
            colors.append('green')
    return colors

# filter dataframe function
def filterReconstructionData(input_df, std_dev_cutoff, maltose_cutoff, maltose_limit, outputDir):
    output_df = input_df.copy()
    # calculate the number of sequences with a mean fluorescence less than G83I and greater than GpA
    output_df = output_df[output_df['std'] < std_dev_cutoff]
    output_df = output_df[output_df[maltose_col] > maltose_cutoff]
    output_df = output_df[output_df[maltose_col] < maltose_limit]
    return output_df

def plotPieChart(input_df, sample, output_dir):
    labels = input_df.columns
    sizes = input_df.values[0]
    # get colors for the pie chart
    colors = getColors(labels)
    #plotPieChart(labels, sizes, colors, sample, outputDir)
    fig, ax = plt.subplots()
    ax.pie(sizes, colors=colors, autopct='%1.1f%%', startangle=90)
    patches, texts, auto = ax.pie(sizes, colors=colors, autopct='%1.1f%%', startangle=90)
    plt.legend(patches, labels, loc="best")
    plt.axis('equal')
    plt.title(f'{sample} design sequences')
    plt.savefig(f'{output_dir}/{sample}_designPieChart.png')
    # add the total number of sequences to the pie chart
    #plt.text(-1.5, 1.5, f'Total Sequences: {totalSeqs}', fontsize=42)
    plt.tight_layout()
    plt.clf()

# read in the reconstructed fluorescence dataframe
reconstructionFile = sys.argv[1]
outputDir = sys.argv[2]

# make the output directory if it doesn't exist
os.makedirs(outputDir, exist_ok=True)

# hardcoded variables
gpa = 'LIIFGVMAGVIGT'
g83i = 'LIIFGVMAIVIGT'
std_dev_cutoff = 5000
maltose_cutoff = -97
maltose_limit = 10000000
maltose_col = 'LB-12H_M9-36H'

# read in the reconstructed fluorescence dataframe
df_fluor = pd.read_csv(reconstructionFile)
df_fluor = calculateMeanFluorescence(df_fluor)

# TODO: might be a good idea to make the trimming part for the pie chart a function
# loop through the samples
samples = df_fluor['Sample'].unique()
sample_list = []
output_df = pd.DataFrame()
for sample in samples:
    df_sample = df_fluor[df_fluor['Sample'] == sample]
    # remove rep1 for GasRight and RightHanded
    if sample == 'G' or sample == 'R':
        df_sample = df_sample.drop(columns=['Rep1-Fluor'])
    # get the index of GpA and G83I from the sequence column 
    gpaIndex, g83iIndex = df_sample[df_sample['Sequence'] == gpa], df_sample[df_sample['Sequence'] == g83i]
    # get the fluorescence from the index
    gpaFluor, g83iFluor = gpaIndex['mean'].values[0], g83iIndex['mean'].values[0]
    df_sample = filterReconstructionData(df_sample, std_dev_cutoff, maltose_cutoff, maltose_limit, outputDir)
    totalSeqs = len(df_sample.index)
    lessThanG83i = len(df_sample[df_sample['mean'] < g83iFluor].index)
    moreThanGpa = len(df_sample[df_sample['mean'] > gpaFluor].index)
    rest = totalSeqs - lessThanG83i - moreThanGpa
    print(f'{sample} has a total of {totalSeqs} sequences. {lessThanG83i} sequences have a mean fluorescence less than G83I and {moreThanGpa} sequences have a mean fluorescence greater than GpA')
    # make a dataframe of number of sequences with a mean fluorescence less than G83I and greater than GpA
    df_pie = pd.DataFrame({'Protein < G83I': lessThanG83i, 'Protein > GpA': moreThanGpa, 'G83I > Protein > GpA': rest}, index=[0])
    # rid of any columns that have a value of 0
    df_pie = df_pie.loc[:, (df_pie != 0).any(axis=0)]
    df_pie.to_csv(f'{outputDir}/{sample}_pieData.csv', index=False)
    # create a pie chart
    plotPieChart(df_pie, sample, outputDir)
    output_df = pd.concat([output_df, df_sample], axis=0)
output_df.to_csv(f'{outputDir}/filteredFluorescence.csv', index=False)

# next figure: mutant stuff with SASA; compare the SASA scores against the fluorescence