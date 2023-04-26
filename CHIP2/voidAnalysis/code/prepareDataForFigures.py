#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   prepareDataForFigures.py
@Time    :   2023/04/26 12:05:22
@Author  :   Gilbert Loiseau 
@Version :   1.0
@Contact :   loiseau@wisc.edu
@License :   (C)Copyright 2023, Gilbert Loiseau
@Desc    :   None
'''

import os, sys, pandas as pd

def getSasaPercentageDifference(mutant_df, polyAla_df):
    output_df = mutant_df.copy()
    # initialize the SasaDifference list
    sasaDiff_list = []
    sasaPercDiff_list = []
    # loop through the mutants 
    for mutant in output_df['Mutant']:
        # get the position of the mutant
        position = output_df[output_df['Mutant'] == mutant]['Position'].values[0]
        # get the ith column of polyAla_df where i is the position of the mutant
        polyAla = polyAla_df.iloc[:, position].values[0]
        # get the mutant sasa
        mutant_sasa = output_df[output_df['Mutant'] == mutant]['Mutant_Position_Sasa'].values[0]
        # get the difference between the polyAla and the mutant sasa
        sasaDiff = polyAla - mutant_sasa
        # append the difference to the sasaDiff list
        sasaDiff_list.append(sasaDiff)
        # get the sasa percentage difference
        sasaPercDiff = (mutant_sasa / polyAla) * 100
        # append the sasa percentage difference to the sasaPercDiff list
        sasaPercDiff_list.append(sasaPercDiff)
    # add the sasaDiff and sasaPercDiff lists to the output_df
    output_df['SasaDifference'] = sasaDiff_list
    output_df['SasaPercDifference'] = sasaPercDiff_list
    return output_df

def getMutantPositionAndAA(df):
    output_df = df.copy()
    # find positions in sequence that are not the same in the mutant
    output_df['Position'] = output_df.apply(lambda row: [i for i in range(len(row['Sequence'])) if row['Sequence'][i] != row['Mutant'][i]], axis=1)
    # check if position is empty
    output_df = output_df[output_df['Position'].apply(lambda x: len(x) > 0)]
    # convert the position column to an integer
    output_df['Position'] = output_df['Position'].apply(lambda x: int(x[0]))
    # get the AA in the sequence for the position
    output_df['WT_AA'] = output_df.apply(lambda row: row['Sequence'][row['Position']], axis=1)
    # concat the start mutant df with the df wt data
    output_df = pd.concat([output_df, df_wt_data], axis=0)
    # remove data where the Position is < 3 or > 17
    output_df = output_df[(output_df['Position'] > 2) & (output_df['Position'] < 18)]
    return output_df

def checkSasaOutsideOfMutatedPosition(mutant_df):
    output_df = mutant_df.copy()
    output_df['Mutant_SASA_no_alanine'] = output_df['Mutant_DimerSasa'] - output_df['Mutant_Position_Sasa']
    # get the sasa without the wt position sasa
    output_df['SASA_no_wt_position'] = output_df['WT_DimerSasa'] - output_df['WT_Position_Sasa']
    # keep the data where the mutant sasa is greater than the sequence sasa
    #output_df = output_df[output_df['Mutant_SASA_no_alanine'] >= output_df['SASA_no_wt_position']]
    # get the difference between the mutant sasa and the sequence sasa
    output_df['DimerSasaDifference'] = output_df['Mutant_SASA_no_alanine'] - output_df['SASA_no_wt_position']
    return output_df

def getCutoffValues(df, analysis_column, output_column):
    output_df = df.copy()
    # add cutoff value to the dataframe
    output_df[output_column] = 'low'
    # check if sasa percentage difference is less than 33%
    output_df.loc[output_df[analysis_column] <= 33, output_column] = 'low'
    # check if sasa percentage difference is greater than 33% and less than 66%
    output_df.loc[(output_df[analysis_column] > 33) & (output_df[analysis_column] <= 66), output_column] = 'medium'
    output_df.loc[output_df[analysis_column] > 66, output_column] = 'high'
    return output_df

# below is a function to apply to the indices that allowed me to set the values based on groupby
# allows me to groupby sequences and then set the values based on the values within the group
# from: https://stackoverflow.com/questions/35046725/pandas-set-value-in-groupby
def applyOnMax(m, value):
    void_data.loc[void_data['DimerSasaDifference'] == m, 'Void_Cutoff'] = value

if __name__ == '__main__':
    # read the command line arguments
    void_data_file = sys.argv[1]
    all_data_file = sys.argv[2]
    polyAla_file = sys.argv[3]

    # read the data files
    void_data = pd.read_csv(void_data_file, dtype={'Interface': str})
    all_data = pd.read_csv(all_data_file, dtype={'Interface': str})
    polyAla_df = pd.read_csv(polyAla_file, sep=',', header=None)

    # multiply the polyAla values by 2 to get the total sasa (currently loads up monomer sasa file)
    polyAla_df = polyAla_df * 2

    # add the sequences that have _ to another dataframe
    df_wt_data = void_data[void_data['Mutant'].str.contains('_')]
    # split by the _ and set the mutant to the first part of the split and the position to the second part of the split without copy warning
    df_wt_data[['Mutant', 'Position']] = df_wt_data['Mutant'].str.split('_', expand=True)
    # set the Position column to an integer
    df_wt_data['Position'] = df_wt_data['Position'].apply(lambda x: int(x))
    # get the AA in the sequence for the position
    df_wt_data['WT_AA'] = df_wt_data.apply(lambda row: row['Sequence'][row['Position']], axis=1)

    # get the mutant position and AA
    void_data = getMutantPositionAndAA(void_data)
    
    # get the sasa percentage difference
    void_data = getSasaPercentageDifference(void_data, polyAla_df)

    # get the monomer without alanine sasa
    void_data = checkSasaOutsideOfMutatedPosition(void_data)

    # categorize the void mutants by DimerSasaDifference
    void_data['Void_Cutoff'] = 'low'
    # set the top 4 DimerSasaDifference values to medium 
    void_data.groupby('Sequence').DimerSasaDifference.nlargest(4).apply(applyOnMax, value='medium')
    # set the top 2 DimerSasaDifference values to high
    void_data.groupby('Sequence').DimerSasaDifference.nlargest(2).apply(applyOnMax, value='high')
    
    # get the cutoff values for the sasa percentage difference
    void_data = getCutoffValues(void_data, 'SasaPercDifference', 'Clash_Cutoff')

    # merge the output_df with the all_data dataframe with the Sequence and Interface columns
    output_df = pd.merge(void_data, all_data[['Sequence', 'replicateNumber', 'Directory']], on='Sequence', how='left')
    # save the output dataframe to a csv file
    output_df.to_csv('sasa_cutoff.csv', index=False)