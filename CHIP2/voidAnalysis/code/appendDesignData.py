import os, sys, pandas as pd

if __name__ == '__main__':
    # get the command line arguments
    input_file = sys.argv[1]
    data_file = sys.argv[2]
    output_file = sys.argv[3]
    output_dir = sys.argv[4]

    # read in the csv file as a dataframe
    df = pd.read_csv(input_file, sep=',', header=0)

    # read in the data file with interface data as string
    data_df = pd.read_csv(data_file, sep=',', header=0, dtype={'Interface': str})

    # define the columns to add to the output dataframe
    columns = ['Sequence', 'Region', 'Total', 'Interface']
    data_df = data_df[columns]

    # merge the data_df with the output_df by the sequence
    df = pd.merge(df, data_df, on='Sequence', how='left')

    # save the dataframe to a csv file
    df.to_csv(f'{output_dir}/{output_file}', index=False)

