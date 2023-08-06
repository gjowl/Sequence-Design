'''
File: /home/loiseau@ad.wisc.edu/github/Sequence-Design/ngsReconstruction/code/controlAnalysis.py
Project: /home/loiseau@ad.wisc.edu/github/Sequence-Design/ngsReconstruction/code
Created Date: Friday August 4th 2023
Author: loiseau
-----
Last Modified: Friday August 4th 2023 1:39:48 pm
Modified By: loiseau
-----
Description: 
This file uses the following as inputs:
    - reconstructed fluorescence dataframe
It identifies the fluorescence of control sequences (marked in column segment as a non-numeric value),
creates a ... (curve?) of the fluorescence of the control sequences, and outputs a dataframe with the
...(something comparison to the for others sequences to controls). It is used specifically for my CHIP2
data for now to determine the designability of geometric regions for membrane proteins (maybe).
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------
'''

import sys, os, pandas as pd, numpy as np, matplotlib.pyplot as plt

# read in the reconstructed fluorescence dataframe
reconstructionFile = sys.argv[1]
outputDir = sys.argv[2]
df_reconstruction = pd.read_csv(reconstructionFile, index_col=0)

# get the control sequences
df_nonControl = df_reconstruction[pd.to_numeric(df_reconstruction['Segments'], errors = 'coerce').notnull()]
# get the control sequences by removing the non-control sequences from the reconstruction dataframe
df_control = df_reconstruction.drop(df_nonControl.index)

samples = df_control['Sample'].unique()

# loop through the samples
sample_list = []
for sample in samples:
    # get the control sequences for that sample
    df_control_sample = df_control[df_control['Sample'] == sample]
    # keep only the columns that contain Rep
    df_control_sample = df_control_sample[df_control_sample.columns[df_control_sample.columns.str.contains('Rep')]]
    # remove any rows that with a 0 value
    #df_control_sample = df_control_sample.loc[(df_control_sample != 0).any(axis=1)]
    df_zeros = df_control_sample[(df_control_sample == 0).any(axis=1)]
    df_control_sample = df_control_sample.drop(df_zeros.index)
    # remove rep1 for GasRight and RightHanded
    if sample == 'G' or sample == 'R':
        df_control_sample = df_control_sample.drop(columns=['Rep1-Fluor'])
    df_control_sample['mean'] = df_control_sample.mean(axis=1)
    df_control_sample['mean'].plot.bar()
    # add the mean to the sample list without the index
    sample_list.append(df_control_sample['mean'])
    # plot the standard deviation as a line on the same plot
    plt.errorbar(x=df_control_sample.index, y=df_control_sample['mean'], yerr=df_control_sample.std(axis=1), fmt='none', c='black')
    plt.xlabel('Sequence')
    plt.ylabel('Fluorescence')
    plt.title(f'{sample} control sequences')
    plt.tight_layout()
    # adjust the x axis labels
    plt.savefig(f'{outputDir}/{sample}_controlHistogram.png')
    plt.clf() 

ax = plt.subplot(111)
y = [4, 9, 2]
print(y)
ind = np.arange(len(sample_list[0]))
print(sample_list[0])
ax.bar(ind-0.2, sample_list[0], width=0.2, color='b', align='center')
ax.bar(ind, sample_list[1], width=0.2, color='g', align='center')
ax.bar(ind+0.2, sample_list[2], width=0.2, color='r', align='center')
# set the x ticks to be the sequence names
ax.set_xticks(ind)
ax.set_xticklabels(df_control_sample.index)
# rotate the x ticks
plt.xticks(rotation=90)
plt.xlabel('Sequence')
plt.ylabel('Fluorescence')
plt.title('Average fluorescence of control sequences separated by sample')
# set the legend
ax.legend(('GAS', 'Left', 'Right'))
#ax.autoscale(tight=True)
plt.savefig(f'{outputDir}/controlHistogram.png')
    





