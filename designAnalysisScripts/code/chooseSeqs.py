import os, sys, pandas as pd, numpy as np, matplotlib.pyplot as plt
import random
from analysisFunctions import plotGeomKde

"""
This script will read in a csv file and a number from the command line, comb through the geometric data, and output a csv file
with the number of sequences for each cluster that can be used for experiments.
"""
# functions
# normalize the geometry data by a given x and y axis
def normalizeGeometry(df, xAxis, yAxis):
    # setup dataframe
    output_df = df.copy()
    # add the xChange and crossChange columns together as a copy of the dataframe
    output_df['geomChange'] = output_df[xAxis] + output_df[yAxis]
    # normalize the xChange and crossChange columns
    output_df['geomChangeNorm'] = (output_df['geomChange'] - output_df['geomChange'].min()) / (output_df['geomChange'].max() - output_df['geomChange'].min())
    return output_df

# makes a list of cutoffs for the data and sorts
def makeCutoffList(num_cutoffs):
    cutoff_list = []
    for i in range(num_cutoffs):
        cutoff_list.append(1/(i+1))
    # sort the cutoff list by smallest to largest
    cutoff_list.sort()
    return cutoff_list

# gets the data for a given cutoff list
def getCutoffData(df, cutoff_list):
    output_df = pd.DataFrame()
    for cutoff in cutoff_list:
        # initialize the cutoff dataframe
        cutoff_df = pd.DataFrame()
        # check if the cutoff is the first cutoff
        if cutoff == cutoff_list[0]:
        # get the data for the cutoff
            cutoff_df = region_df[region_df['geomChangeNorm'] <= cutoff]
        elif cutoff != cutoff_list[len(cutoff_list)-1]:
            cutoff_df = region_df[(region_df['geomChangeNorm'] > cutoff_list[cutoff_list.index(cutoff) - 1]) & (region_df['geomChangeNorm'] <= cutoff)]
        else:
            cutoff_df = region_df[region_df['geomChangeNorm'] > cutoff_list[cutoff_list.index(cutoff) - 1]]
        # randomly sample the cutoff dataframe
        seqs_per_cutoff = int(numSeqs / len(cutoff_list))
        try:
            cutoff_df = cutoff_df.sample(n=seqs_per_cutoff, random_state=seed)
        except ValueError:
            cutoff_df = cutoff_df.sample(n=len(cutoff_df), random_state=seed)
        # append the cutoff dataframe to the output dataframe using concat
        output_df = pd.concat(objs=[output_df, cutoff_df], axis=0)
    return output_df

if __name__ == "__main__":
    # read in the data from command line
    data = sys.argv[1]
    output_dir = sys.argv[2]
    kde_file = sys.argv[3]
    numSeqs = int(sys.argv[4])
    seed = random.randint(0, 1000)
    num_cutoffs = int(sys.argv[5])

    # make the output directory
    os.makedirs(name=output_dir, exist_ok=True)

    # read in the data
    df = pd.read_csv(data, dtype={'Interface': str})
    df = df[df['Total'] < -10]

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
        region_df = normalizeGeometry(region_df, 'endXShift', 'endCrossingAngle')
        # setup a cutoff list for the region depending on the number of cutoffs
        cutoff_list = makeCutoffList(num_cutoffs)
        region_output_df = getCutoffData(region_df, cutoff_list)
        # check if the output dataframe is less than the number of sequences (some regions may be too small to get the number of sequences per cutoff)
        if len(region_output_df) < numSeqs:
            # get the difference between the number of sequences and the length of the output dataframe
            diff = numSeqs - len(region_output_df)
            diff_df = region_df.sample(n=diff, random_state=seed)
            region_output_df = pd.concat(objs=[region_output_df, diff_df], axis=0)
        # output the data to a csv file
        #region_output_df.to_csv(f'{region_dir}/seqs.csv', index=False)
        output_df = pd.concat(objs=[output_df, region_output_df], axis=0)
    output_df.to_csv(f'{output_dir}/seqs.csv', index=False)
    plotGeomKde(df_kde, output_df, "Total", output_dir, "endXShift", "endCrossingAngle")