import os, sys, pandas as pd, numpy as np, matplotlib.pyplot as plt
import random
from analysisFunctions import plotGeomKde

"""
This script will read in a csv file and a number from the command line, comb through the geometric data, and output a csv file
with the number of sequences for each cluster that can be used for experiments.
"""
# functions
# normalize the geometry data by a given x and y axis
def normalizeGeometry(df, xAxis, yAxis, column_name):
    # setup dataframe
    output_df = df.copy()
    # add the xChange and crossChange columns together as a copy of the dataframe
    output_df[column_name] = output_df[xAxis] + output_df[yAxis]
    # normalize the xChange and crossChange columns
    output_df[column_name] = (output_df[column_name] - output_df[column_name].min()) / (output_df[column_name].max() - output_df[column_name].min())
    return output_df

def normalizeColumn(df, column):
    # setup dataframe
    output_df = df.copy()
    # normalize the column
    output_df[f'{column}Norm'] = (output_df[column] - output_df[column].min()) / (output_df[column].max() - output_df[column].min())
    return output_df

# makes a list of cutoffs for the data and sorts
def makeCutoffList(num_cutoffs):
    cutoff_list = []
    cutoff_percent = 1 / num_cutoffs
    for i in range(1,num_cutoffs+1):
        cutoff_list.append(cutoff_percent * i)
    # sort the cutoff list by smallest to largest
    cutoff_list.sort()
    return cutoff_list

# gets the data for a given cutoff list
def getCutoffData(df, cutoff_list, num_seqs, column):
    output_df = pd.DataFrame()
    for cutoff in cutoff_list:
        # initialize the cutoff dataframe
        cutoff_df = pd.DataFrame()
        # randomly sample the cutoff dataframe 
        # check if the cutoff is the first cutoff
        if cutoff == cutoff_list[0]:
        # get the data for the cutoff
            cutoff_df = region_df[region_df[column] <= cutoff]
        elif cutoff != cutoff_list[len(cutoff_list)-1]:
            cutoff_df = region_df[(region_df[column] > cutoff_list[cutoff_list.index(cutoff) - 1]) & (region_df[column] <= cutoff)]
        else:
            cutoff_df = region_df[region_df[column] > cutoff_list[cutoff_list.index(cutoff) - 1]]
        # randomly sample the cutoff dataframe
        try:
            cutoff_df = cutoff_df.sample(n=num_seqs, random_state=seed)
        except ValueError:
            # if not enough sequences, defer to the energy cutoff and just get all of the sequences with good energy
            cutoff_df = region_df[region_df[column] <= cutoff]
            cutoff_df = cutoff_df.sample(n=len(cutoff_df), random_state=seed)
        # append the cutoff dataframe to the output dataframe using concat
        output_df = pd.concat(objs=[output_df, cutoff_df], axis=0)
    return output_df

if __name__ == "__main__":
    # read in the data from command line
    data = sys.argv[1]
    output_dir = sys.argv[2]
    kde_file = sys.argv[3]
    num_seqs = int(sys.argv[4])
    seed = random.randint(0, 1000)
    num_cutoffs = int(sys.argv[5])

    # make the output directory
    os.makedirs(name=output_dir, exist_ok=True)

    # read in the data
    df = pd.read_csv(data, dtype={'Interface': str})
    df = df[df['Total'] < -5]
    energy_column = 'Total'

    # read in kde data as a dataframe
    df_kde = pd.read_csv(kde_file)

    # loop through the regions
    output_df = pd.DataFrame()
    for region in df['Region'].unique():
        # initialize the output dataframe
        region_output_df = pd.DataFrame()
        # get the data for the region
        region_df = df[df['Region'] == region]
        if region == 'GAS':
            # filter out the data for GASright to be more stringent
            region_df = region_df.loc[(region_df['endXShift'] < 7.5) & (region_df['endCrossingAngle'] > -47)]
        elif region == 'Right':
            region_df = region_df.loc[(region_df['endXShift'] < 9)]
        elif region == 'Left':
            region_df = region_df.loc[(region_df['endXShift'] < 10)]
        # normalize the geometry data
        geom_column_name = 'geomChangeNorm'
        region_df = normalizeGeometry(region_df, 'endXShift', 'endCrossingAngle', geom_column_name)
        # normalize the energy data
        region_df = normalizeColumn(region_df, energy_column)
        # setup a cutoff list for the region depending on the number of cutoffs
        cutoff_list = makeCutoffList(num_cutoffs)
        norm_energy_column = f'{energy_column}Norm'
        region_df[norm_energy_column] = pd.qcut(region_df[norm_energy_column], q=[0, 0.3333, 0.6666, 1], labels=False)
        region_df[geom_column_name] = pd.qcut(region_df[geom_column_name], q=[0, 0.3333, 0.6666, 1], labels=False)
        region_output_df = pd.DataFrame()
        for energy_bin in region_df[norm_energy_column].unique():
            for geom_bin in region_df[geom_column_name].unique():
                seqs_per_cutoff = int(num_seqs / len(cutoff_list) / len(cutoff_list))
                # get the data for the energy and geometry bins
                bin_df = region_df[(region_df[norm_energy_column] == energy_bin) & (region_df[geom_column_name] == geom_bin)]
                # randomly sample the bin dataframe
                bin_df = bin_df.sample(n=seqs_per_cutoff, random_state=seed)
                region_output_df = pd.concat(objs=[region_output_df, bin_df], axis=0)
        # sort the region output dataframe by the energy column
        region_output_df = region_output_df.sort_values(by=energy_column, ascending=True)
        # output the region data to a csv file
        region_output_df.to_csv(f'{output_dir}/{region}_seqs.csv', index=False)
        output_df = pd.concat(objs=[output_df, region_output_df], axis=0)
    # sort the output dataframe by the region column and energy column
    output_df = output_df.sort_values(by=['Region', energy_column], ascending=True)
    # output the data to a csv file
    output_df.to_csv(f'{output_dir}/seqs.csv', index=False)
    plotGeomKde(df_kde, output_df, "Total", output_dir, "endXShift", "endCrossingAngle")