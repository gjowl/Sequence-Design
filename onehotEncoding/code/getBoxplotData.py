import os, sys, pandas as pd
from boxplot_per_AA import *

# gets the average, median, standard deviation, range, and number of data points for each AA
def getStats(df_data, xAxis, yAxis):
    # calculate the stats
    df_stats = df_data.groupby(xAxis)[yAxis].agg(['mean', 'median', 'std', 'min', 'max', 'count'])
    # add the positions to the dataframe from the data dataframe
    df_stats['Position'] = df_data['Position'][0]
    # reset the index
    df_stats.reset_index(inplace=True)
    # output the stats to a csv file
    #df_stats.to_csv(f'{output_dir}/{file_name}_stats.csv', index=False)
    return df_stats

if __name__ == '__main__':
    # get the input directory
    input_dir = sys.argv[1]

    # axes to plot
    xAxis = 'AA'
    yAxis = 'PercentGpa'

    # initialize the dataframe
    df_data = pd.DataFrame()

    # loop through the directories in the input directory
    for directory in os.listdir(input_dir):
        # for each directory, loop through the directories
        position_dir = f'{input_dir}/{directory}'
        output_df = pd.DataFrame()
        for position in os.listdir(position_dir):
            # for each directory, loop through the files
            aa_dir = f'{position_dir}/{position}'
            data_dir = f'{directory}/data'
            # create the output directory for plots
            os.makedirs(data_dir, exist_ok=True)
            # loop through files ending in csv
            for file in os.listdir(aa_dir):
                if file.endswith('.csv'):
                    # read in the file
                    df_data = pd.read_csv(f'{aa_dir}/{file}', dtype={'Interface': str})
                    # find all columns with AA in the name and combine them into one column
                    aa_cols = [col for col in df_data.columns if 'AA' in col]
                    df_data['AA'] = df_data[aa_cols].apply(lambda x: ''.join(x), axis=1)
                    # get the stats for all the data
                    df_stats = getStats(df_data, xAxis, yAxis)
                    output_df = pd.concat([output_df, df_stats], ignore_index=True)
        # output the stats to a csv file
        output_df.to_csv(f'{data_dir}/{directory}_stats.csv', index=False)
                    ## loop through the regions and get the stats for each region
                    #for region in df_data['Region'].unique():
                    #    df_region = df_data[df_data['Region'] == region]
                    #    # make sure dataframe is not empty
                    #    if df_region.empty or len(df_region) < 10:
                    #        continue
                    #    # remove data for any positions that have less than 10 data points
                    #    df_region = df_region.groupby('Position').filter(lambda x: len(x) >= 10)
                    #    # create the output directory for region
                    #    region_dir = f'{output_dir}/{region}'
                    #    os.makedirs(region_dir, exist_ok=True)
                    #    plotBoxplot(df_region, region_dir, file_name, xAxis, yAxis, yMin, yMax, file_name)