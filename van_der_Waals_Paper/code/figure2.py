'''
File: /home/loiseau@ad.wisc.edu/github/Sequence-Design/van_der_Waals_Paper/code/figure2.py
Project: /home/loiseau@ad.wisc.edu/github/Sequence-Design/van_der_Waals_Paper/code
Created Date: Wednesday September 20th 2023
Author: loiseau
-----
Last Modified: Wednesday September 20th 2023 12:19:38 pm
Modified By: loiseau
-----
Description:
This file contains the code to generate figure 2 of the paper.

Input:
    - 

'''

import os, sys, pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns

pieColors = ['red', 'green']

def makePieChart(input_df, col, outputDir):
    sample = input_df['Sample'].unique()[0]
    # get the values for the pie chart
    lessThanG83I = len(input_df[input_df[col] < monomerPercentGpA]) 
    moreThanG83I = len(input_df[input_df[col] > monomerPercentGpA])
    # make a dataframe of number of sequences with a mean fluorescence less than G83I and greater than GpA
    df_pie = pd.DataFrame({'Protein < Monomer': lessThanG83I, 'Protein > Monomer': moreThanG83I}, index=[0])
    df_pie.to_csv(f'{outputDir}/{sample}_pieData.csv', index=False)
    plotPieChart(df_pie, sample, outputDir)

def plotPieChart(input_df, sample, output_dir):
    labels = input_df.columns
    sizes = input_df.values[0]
    fig, ax = plt.subplots()
    ax.pie(sizes, colors=pieColors, autopct='%1.1f%%', startangle=90)
    patches, texts, auto = ax.pie(sizes, colors=pieColors, autopct='%1.1f%%', startangle=90)
    plt.legend(patches, labels, loc="best")
    plt.axis('equal')
    plt.title(f'{sample} design sequences')
    plt.savefig(f'{output_dir}/{sample}_designPieChart.png')
    # add the total number of sequences to the pie chart
    totalSeqs = sum(sizes)
    plt.text(-0.5, 1.2, f'Total number of sequences: {totalSeqs}', fontsize=12)
    plt.tight_layout()
    plt.clf()

def plotPercentSeqs(input_df, col, output_dir):
    sns.set_style("whitegrid")
    sns.boxplot(x="Sample", y=col, hue="Type",data=input_df, color='green')
    sns.swarmplot(x="Sample", y=col, hue="Type", data=input_df, color='0', dodge=True, size=1)
    plt.xlabel('Sample')
    plt.ylabel('Percent GpA')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/percentSeqs.png')
    plt.clf()

# read in the command line arguments
inputFile = sys.argv[1]
kdeFile = sys.argv[2]
outputDir = "figure2"
os.makedirs(outputDir, exist_ok=True)
# TODO: combine the wt and mutant dataframes into one dataframe before running this script; makes it easier to plot the data

# hardcoded monomer percent GpA (TOXGREEN G83I is 25%) 
monomerPercentGpA = 0.40
col = "PercentGpA_transformed"

# read in the data
df = pd.read_csv(inputFile, sep=',')
df = df[df[col] < 2]

# loop through the different samples
for sample in df['Sample'].unique():
    # get the data for the sample
    df_sample = df[df['Sample'] == sample]
    # make the pie chart
    pieDir = f'{outputDir}/pieCharts'
    os.makedirs(pieDir, exist_ok=True)
    makePieChart(df_sample, col, pieDir)

# make the percentage seqs plot
percentSeqsDir = f'{outputDir}/percentSeqs'
os.makedirs(percentSeqsDir, exist_ok=True)
plotPercentSeqs(df, col, percentSeqsDir)
# make the fluor vs Geometry plot
fluorVsGeometryDir = f'{outputDir}/fluorVsGeometry'
os.makedirs(fluorVsGeometryDir, exist_ok=True)
plotFluorVsGeometry(df, col, fluorVsGeometryDir)
