'''
Run as: python3 prepareDataFile.py {dataFile} {interfaceFile}
'''

import os, sys, pandas as pd

if __name__ == '__main__':
    # read the command line arguments
    data_file = sys.argv[1]
    interface_file = sys.argv[2]

    # read in the data file
    df = pd.read_csv(data_file, sep=',', dtype={'Interface': str})
    # add LLL and ILI to the sequence
    df['Sequence'] = 'LLL' + df['Sequence'] + 'ILI'

    # read in the interface file
    df_interface = pd.read_csv(interface_file, sep=',', dtype={'Interface': str})

    # loop through the entire dataframe
    for sequence in df['Sequence'].unique():
        # find the interface for that sequence
        interface = df_interface[df_interface['Sequence'] == sequence]['Interface'].values[0]
        # replace the interface in the dataframe
        df.loc[df['Sequence'] == sequence, 'Interface'] = interface
    # output the dataframe to a csv
    df.to_csv(f'{data_file}_fixedInterface.csv', index=False)