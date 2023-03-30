import os, sys, pandas as pd

# gets the average, median, standard deviation, range, and number of data points for each AA
def getStats(df_data, xAxis, yAxis, output_dir):
    # get the average, median, standard deviation, range, and number of data points for each AA
    df_stats = df_data.groupby(xAxis).agg({yAxis: ['mean', 'median', 'std', 'min', 'max', 'count']})
    # reset the index
    df_stats.reset_index(inplace=True)
    # output the stats to a csv file
    df_stats.to_csv(f'{output_dir}/stats.csv', index=False)

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
                    # create the output directory for the AA
                    os.makedirs(output_dir, exist_ok=True)
                    # get the file name without the extension
                    file_name = os.path.splitext(file)[0]
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