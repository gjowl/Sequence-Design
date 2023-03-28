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
    #yAxis = 'PercentGpa'
    yAxis = 'Total'
    yMin = -55
    yMax = 0 
    geom_list = ['endXShift', 'endCrossingAngle', 'endAxialRotation', 'endZShift']
    norm_cols = [f'{col}Norm' for col in geom_list]
    colors = ['red', 'blue', 'green', 'orange']

    # loop through the directories in the input directory
    for directory in os.listdir(input_dir):
        # for each directory, loop through the files
        aa_dir = f'{input_dir}/{directory}'
        # loop through files ending in csv
        for file in os.listdir(aa_dir):
            if file.endswith('.csv'):
                # read in the file
                df_data = pd.read_csv(f'{aa_dir}/{file}', dtype={'Interface': str})
                # add the region column
                df_data = addRegion(df_data)
                # combine the aa1 and aa2 columns
                df_data['AA'] = df_data['AA1'] + df_data['AA2']
                # keep only data where the yAxis value is < the yMax
                df_data = df_data[df_data[yAxis] < yMax]
                # get the file name without the extension
                file_name = os.path.splitext(file)[0]
                # create the output directory for plots
                plot_dir = f'{aa_dir}/{file_name}_plots'
                os.makedirs(plot_dir, exist_ok=True)
                # plot the boxplot for all of the data
                plotBoxplot(df_data, plot_dir, file_name, xAxis, yAxis, yMin, yMax, 'all')
                # loop through the regions and create a boxplot for each
                for region in df_data['Region'].unique():
                    df_region = df_data[df_data['Region'] == region]
                    # make sure dataframe is not empty
                    if df_region.empty or len(df_region) < 10:
                        continue
                    print(df_region)
                    # remove data for any positions that have less than 10 data points
                    df_region = df_region.groupby('Position').filter(lambda x: len(x) >= 10)
                    plotBoxplot(df_region, plot_dir, file_name, xAxis, yAxis, yMin, yMax, region)
                    # loop through the amino acids and positions
                    for aa1 in df_region['AA1'].unique():
                        aa1_df = df_region[df_region['AA1'] == aa1]
                        # create the output directory for region
                        region_dir = f'{plot_dir}/{region}'
                        os.makedirs(region_dir, exist_ok=True)
                        # make sure the plot directory is empty 
                        for file in os.listdir(region_dir):
                            os.remove(f'{region_dir}/{file}')
                        for aa2 in aa1_df['AA2'].unique():
                            aa2_df = aa1_df[aa1_df['AA2'] == aa2]
                            # normalize the geometries column
                            aa2_df = normalizeGeometry(aa2_df, geom_list)
                            # plot the boxplot for each position
                            aa = f'{aa1}_{aa2}'
                            plotMultiBoxPlot(aa2_df, region_dir, aa, xAxis, norm_cols, colors, f'{aa1}_{aa2}_{region}')