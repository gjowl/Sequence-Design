import os, sys, pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# break down the into regions
def addRegion(df):
    # loop through dataframe rows and break down into regions
    for index, row in df.iterrows():
        # check the xShift value
        if row['startXShift'] <= 7.5:
            # add region column GAS
            df.loc[index, 'Region'] = 'GAS'
        elif row['startXShift'] > 7.5 and row['startCrossingAngle'] < 0:
            # add region column GAS
            df.loc[index, 'Region'] = 'Right'
        elif row['startXShift'] > 7.5 and row['startCrossingAngle'] > 0:
            # add region column Left
            df.loc[index, 'Region'] = 'Left'
    return df

def compile_data(input_dir):
    # initialize the dataframe 
    df_data = pd.DataFrame()
    for file in os.listdir(input_dir):
        # read in the file if not named compiledData.csv
        if file != 'compiledData.csv' and file.endswith('csv'):
            df_pos = pd.read_csv(f'{aa_dir}/{file}', dtype={'Interface': str})
            # add the position data to the main dataframe
            df_data = pd.concat([df_data, df_pos], ignore_index=True)
    return df_data

def normalizeGeometry(df, geomList):
    # setup dataframe
    output_df = df.copy()
    # loop through the geometry columns
    for geom in geomList:
        norm_geom = f'{geom}Norm'
        # normalize the xChange and crossChange columns
        output_df[norm_geom] = (output_df[geom] - output_df[geom].min()) / (output_df[geom].max() - output_df[geom].min())
    return output_df

def plotBoxplot(df_data, output_dir, aa, xAxis, yAxis, output_name):
    # create a boxplot for each region using plt
    #df_data.boxplot(column=yAxis, by=xAxis, grid=False)
    mdf = pd.melt(df_data, id_vars=[xAxis], value_vars=[yAxis])
    fig, ax = plt.subplots(figsize=(10, 6))
    ax = sns.boxplot(x=xAxis, y='value', hue='variable', data=mdf, palette='Greens')
    # remove the legend
    ax.legend_.remove()
    # set the y axis value range
    plt.ylim(0, 130)
    # set the title
    plt.title(f'Boxplot for {aa}: {output_name}')
    # set the y label
    plt.ylabel(f'{yAxis}')
    # save the boxplot
    plt.savefig(f'{output_dir}/{yAxis}_{output_name}.png')
    # close the plot
    plt.close()

def plotMultiBoxPlot(df_data, output_dir, aa, xAxis, yAxis_list, colors, output_name):
    mdf = pd.melt(df_data, id_vars=[xAxis], value_vars=yAxis_list)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax = sns.boxplot(x=xAxis, y='value', hue='variable', data=mdf)
    # move the legend to the bottom of the plot below the x label
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=5)
    # set the y axis value range
    plt.ylim(0, 1)
    # set the title
    plt.title(f'Boxplot for {aa}')
    # set the y label
    plt.ylabel(f'Normalized Geometries')
    # save the boxplot
    plt.savefig(f'{output_dir}/{output_name}_multiplot.png')
    # close the plot
    plt.close()

if __name__ == '__main__':
    # get command line arguments
    input_dir = sys.argv[1]

    # axes to plot
    xAxis = 'Position'
    yAxis = 'PercentGpa'
    geom_list = ['xShift', 'crossingAngle', 'axialRotation', 'zShift']
    norm_cols = [f'{col}Norm' for col in geom_list]
    colors = ['red', 'blue', 'green', 'orange']

    # loop through the directories in the input directory
    for directory in os.listdir(input_dir):
        # for each directory, loop through the files
        aa_dir = f'{input_dir}/{directory}'
        df_data = compile_data(aa_dir)
        # add the region column
        df_data = addRegion(df_data)
        # save the dataframe
        df_data.to_csv(f'{aa_dir}/compiledData.csv', index=False)
        # get the amino acid name
        aa = df_data['AA'][0]
        # create the output directory for plots
        plot_dir = f'{aa_dir}/plots'
        os.makedirs(plot_dir, exist_ok=True)
        # make sure the plot directory is empty 
        for file in os.listdir(plot_dir):
            os.remove(f'{plot_dir}/{file}')
        # plot the boxplot for all of the data
        plotBoxplot(df_data, plot_dir, aa, xAxis, yAxis, 'All')
        # loop through the regions and create a boxplot for each
        for region in df_data['Region'].unique():
            df_region = df_data[df_data['Region'] == region]
            # remove data for any positions that have less than 10 data points
            df_region = df_region.groupby('Position').filter(lambda x: len(x) >= 10)
            # normalize the geometries column
            df_region = normalizeGeometry(df_region, geom_list)
            plotBoxplot(df_region, plot_dir, aa, xAxis, yAxis, region)
            # plot the multi boxplot
            plotMultiBoxPlot(df_region, plot_dir, aa, xAxis, norm_cols, colors, region)
            # output the data to a csv file
            df_region.to_csv(f'{plot_dir}/{region}_data.csv', index=False)