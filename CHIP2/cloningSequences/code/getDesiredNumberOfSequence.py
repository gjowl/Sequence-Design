#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   getDesiredNumberOfSequence.py
@Time    :   2023/05/05 15:07:12
@Author  :   Gilbert Loiseau 
@Version :   1.0
@Contact :   loiseau@wisc.edu
@License :   (C)Copyright 2023, Gilbert Loiseau
@Desc    :   None
'''

import sys, os, pandas as pd

def getColonyNumbers(number_of_sequences, segment):
    output_df = pd.DataFrame()
    # get the number of colonies for the desired dilutions
    x100 = number_of_sequences 
    x1000 = number_of_sequences / 10
    # add the number of colonies to the dataframe using concat
    output_df = pd.concat([output_df, pd.DataFrame({'Segment': [segment], 'Dilution': ['x100'], 'Number of colonies': [x100]})])
    output_df = pd.concat([output_df, pd.DataFrame({'Segment': [segment], 'Dilution': ['x1000'], 'Number of colonies': [x1000]})])
    # return the dataframe
    return output_df

# read in the CHIP file
chip = sys.argv[1]
output_file = sys.argv[2]

# read in the CHIP file as a dataframe
chip_df = pd.read_csv(chip, sep=",")

# loop through the segments and get the desired number of sequences
output_df = pd.DataFrame()
for segment in chip_df['Segment'].unique():
    # get the number of sequences in the segment
    number_of_sequences = chip_df[chip_df['Segment'] == segment].shape[0]
    # get the desired number of colonies per plate
    segment_df = getColonyNumbers(number_of_sequences, segment) 
    # concatenate the dataframes
    output_df = pd.concat([output_df, segment_df])

# write the output dataframe to a file
output_df.to_csv(output_file, sep=",", index=False)

