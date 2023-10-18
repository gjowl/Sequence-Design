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
import statsmodels.formula.api as sfa
import statsmodels.api as sa

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
    #plt.legend(patches, labels, loc="best")
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
    sns.boxplot(x="Sample", y=col, hue="Type",data=input_df, color='green', fliersize=2)
    sns.swarmplot(x="Sample", y=col, hue="Type", data=input_df, color='0', dodge=True, size=2)
    # sort by sample
    input_df = input_df.sort_values(by=['Sample'])
    calculate_pvalues(input_df)
    for i, sample in enumerate(input_df['Sample'].unique()):
        # separate the dataframe by mutant and wt
        df_wt, df_mutant = input_df[input_df['Type'] == 'WT'], input_df[input_df['Type'] == 'Mutant']
        plt.text(i-.25, -.07, len(df_wt[df_wt['Sample'] == sample]), ha='left')
        plt.text(i+.25, -.07, len(df_mutant[df_mutant['Sample'] == sample]), ha='right')
    # remove the legend
    plt.legend([],[], frameon=False)
    plt.xlabel('Sample')
    plt.ylabel('Percent GpA')
    # set the y axis limits
    # TODO: add the pvalue to the plot
    plt.ylim(bottom=0)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/percentSeqs.png')
    plt.clf()

# function for calculating the pvalues
def calculate_pvalues(df):
    for sample in df['Sample'].unique():
        df_sample = df[df['Sample'] == sample]
        #df_sample = df_sample[['Type', 'PercentGpA_transformed']]
        lm = sfa.ols('PercentGpA_transformed ~ Type', data=df_sample).fit()
        anova = sa.stats.anova_lm(lm)
        # print the pvalue
        print(sample, anova['PR(>F)'][0])

#def plotFluorBarGraph(input_df, col, output_dir):
#    sns.set_style("whitegrid")
#    sns.barplot(x="Sample", y=col, hue="Type", data=input_df, color='green')
#    # remove the legend
#    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
#    plt.xlabel('Sample')
#    plt.ylabel('Percent GpA')
#    plt.tight_layout()
#    plt.savefig(f'{output_dir}/percentSeqs.png')
#    plt.clf()

# read in the command line arguments
inputFile = sys.argv[1]
#kdeFile = sys.argv[2]
outputDir = "figure2"
os.makedirs(outputDir, exist_ok=True)
# TODO: combine the wt and mutant dataframes into one dataframe before running this script; makes it easier to plot the data

# hardcoded monomer percent GpA (TOXGREEN G83I is 25%) 
monomerPercentGpA = 0.35
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

# make bar graph for number of sequences with fluorescence
#fluorDir = f'{outputDir}/fluorBarGraphs'
#os.makedirs(fluorDir, exist_ok=True)
#plotFluorBarGraph(df, col, fluorDir)

# make the percentage seqs plot
percentSeqsDir = f'{outputDir}/percentSeqs'
os.makedirs(percentSeqsDir, exist_ok=True)
plotPercentSeqs(df, col, percentSeqsDir)

## make the fluor vs Geometry plot
#fluorVsGeometryDir = f'{outputDir}/fluorVsGeometry'
#os.makedirs(fluorVsGeometryDir, exist_ok=True)
#plotFluorVsGeometry(df, col, fluorVsGeometryDir)
