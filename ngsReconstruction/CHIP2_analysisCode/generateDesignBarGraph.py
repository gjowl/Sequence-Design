'''
File: d:\github\Sequence-Design\ngsReconstruction\CHIP2_analysisCode\generateDesignBarGraph.py
Project: d:\github\Sequence-Design\ngsReconstruction\CHIP2_analysisCode
Created Date: Saturday August 5th 2023
Author: gjowl
-----
Last Modified: Saturday August 5th 2023 3:39:50 pm
Modified By: gjowl
-----
Description: ...add description here... 
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------
'''

import sys, os, pandas as pd, numpy as np, matplotlib.pyplot as plt

# read in the reconstructed fluorescence dataframe
reconstructionFile = sys.argv[1]
outputDir = sys.argv[2]
gpa = 'LIIFGVMAGVIGT'
g83i = 'LIIFGVMAIVIGT'
df_reconstruction = pd.read_csv(reconstructionFile, index_col=0)

# get the design sequences
df_design = df_reconstruction[pd.to_numeric(df_reconstruction['Segments'], errors = 'coerce').notnull()]
samples = df_design['Sample'].unique()

# loop through the samples
sample_list = []
for sample in samples:
    # get the design sequences for that sample
    df_design_sample = df_design[df_design['Sample'] == sample]
    # keep only the columns that contain Rep
    df_design_sample = df_design_sample[df_design_sample.columns[df_design_sample.columns.str.contains('Rep')]]
    # remove any rows that with a 0 value
    #df_design_sample = df_design_sample.loc[(df_design_sample != 0).any(axis=1)]
    df_zeros = df_design_sample[(df_design_sample == 0).any(axis=1)]
    df_design_sample = df_design_sample.drop(df_zeros.index)
    # remove rep1 for GasRight and RightHanded
    if sample == 'G' or sample == 'R':
        df_design_sample = df_design_sample.drop(columns=['Rep1-Fluor'])
    df_design_sample['mean'] = df_design_sample.mean(axis=1)
    df_design_sample = df_design_sample.sort_values(by=['mean'], ascending=True)
    df_design_sample['mean'].plot.bar()
    # add the mean to the sample list without the index
    sample_list.append(df_design_sample['mean'])
    # get the fluorescence of GpA and G83I by index
    #gpaIndex = df_reconstruction.index.get_loc(gpa)
    #g83iIndex = df_reconstruction.index.get_loc(g83i)

    # put a horizontal line at the mean of GpA and G83I
    plt.axhline(y=30000, color='g', linestyle='-', label='GpA mean')
    plt.axhline(y=20000, color='r', linestyle='-', label='G83I mean')
    # plot the standard deviation as a line on the same plot
    plt.errorbar(x=df_design_sample.index, y=df_design_sample['mean'], yerr=df_design_sample.std(axis=1), fmt='none', c='black')
    plt.xlabel('Sequence')
    plt.ylabel('Fluorescence')
    plt.title(f'{sample} design sequences')
    # change font size of x axis labels
    plt.xticks(fontsize=2)
    plt.tight_layout()
    # adjust the x axis labels
    plt.savefig(f'{outputDir}/{sample}_designHistogram.png')
    plt.clf() 

ax = plt.subplot(111)
ind = np.arange(len(sample_list[0]))
ax.bar(ind-0.2, sample_list[0], width=0.2, color='b', align='center')
ax.bar(ind, sample_list[1], width=0.2, color='g', align='center')
ax.bar(ind+0.2, sample_list[2], width=0.2, color='r', align='center')
# set the x ticks to be the sequence names
ax.set_xticks(ind)
ax.set_xticklabels(df_design_sample.index)
# rotate the x ticks
plt.xticks(rotation=90)
plt.xlabel('Sequence')
plt.ylabel('Fluorescence')
plt.title('Average fluorescence of design sequences separated by sample')
# set the legend
ax.legend(('GAS', 'Left', 'Right'))
#ax.autoscale(tight=True)
plt.savefig(f'{outputDir}/designHistogram.png')