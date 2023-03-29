import os, sys, pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from boxplot_per_AA import *

if __name__ == '__main__':
    # get command line arguments
    input_dir = sys.argv[1]

    # axes to plot
    xAxis = 'AA'
    yAxis = 'PercentGpa'
    #yAxis = 'Total'
    yMin = -55
    yMax = 0 
    geom_list = ['endXShift', 'endCrossingAngle', 'endAxialRotation', 'endZShift']
    norm_cols = [f'{col}Norm' for col in geom_list]
    colors = ['red', 'blue', 'green', 'orange']

    # loop through the directories in the input directory
    for directory in os.listdir(input_dir):
        # for each directory, loop through the directories
        position_dir = f'{input_dir}/{directory}'
        for position in os.listdir(position_dir):
            # for each directory, loop through the files
            aa_dir = f'{position_dir}/{position}'
            plot_dir = f'{directory}/plots'
            # create the output directory for plots
            os.makedirs(plot_dir, exist_ok=True)
            # loop through files ending in csv
            for file in os.listdir(aa_dir):
                if file.endswith('.csv'):
                    # read in the file
                    df_data = pd.read_csv(f'{aa_dir}/{file}', dtype={'Interface': str})
                    # add the region column
                    df_data = addRegion(df_data)
                    # find all columns with AA in the name and combine them into one column
                    aa_cols = [col for col in df_data.columns if 'AA' in col]
                    df_data['AA'] = df_data[aa_cols].apply(lambda x: ''.join(x), axis=1)
                    # get the first character of the AA column
                    aa = df_data['AA'][0][0]
                    # make a plot directory for this AA
                    output_dir = f'{plot_dir}/{aa}'
                    # create the output directory for the AA
                    os.makedirs(output_dir, exist_ok=True)
                    # keep only data where the yAxis value is < the yMax
                    df_data = df_data[df_data[yAxis] < yMax]
                    # check if the dataframe is empty
                    if df_data.empty:
                        continue
                    # get the file name without the extension
                    file_name = os.path.splitext(file)[0]
                    # plot the boxplot for all of the data
                    plotBoxplot(df_data, output_dir, file_name, xAxis, yAxis, yMin, yMax, file_name)
                    # loop through the regions and create a boxplot for each
                    for region in df_data['Region'].unique():
                        df_region = df_data[df_data['Region'] == region]
                        # make sure dataframe is not empty
                        if df_region.empty or len(df_region) < 10:
                            continue
                        # remove data for any positions that have less than 10 data points
                        df_region = df_region.groupby('Position').filter(lambda x: len(x) >= 10)
                        # create the output directory for region
                        region_dir = f'{output_dir}/{region}'
                        os.makedirs(region_dir, exist_ok=True)
                        plotBoxplot(df_region, region_dir, file_name, xAxis, yAxis, yMin, yMax, file_name)
                    # the below can plot the boxplots for each region, for a set of y values, but I don't need it yet
                    #    # create the output directory for region
                    #    region_dir = f'{plot_dir}/{region}'
                    #    os.makedirs(region_dir, exist_ok=True)
                    #    # make sure the plot directory is empty 
                    #    for file in os.listdir(region_dir):
                    #        os.remove(f'{region_dir}/{file}')
                    #    # loop through the amino acids and positions
                    #    aa_df = pd.DataFrame()
                    #    for col in aa_cols:
                    #        # loop through the unique amino acids
                    #        for aa in df_region[col].unique():
                    #            # get the data for the amino acid
                    #            aa_df = df_region[df_region[col] == aa]
                    #            aa_df = normalizeGeometry(aa_df, geom_list)
                    #            # plot the boxplot for each position
                    #            plotMultiBoxPlot(aa_df, region_dir, aa, xAxis, norm_cols, colors, f'{aa}_{region}')
                    #            print(aa_df)