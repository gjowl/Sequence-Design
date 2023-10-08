'''
File: d:\github\Sequence-Design\CHIP2\analyses\figureMaking\code\replaceInterfaceColumn.py
Project: d:\github\Sequence-Design\CHIP2\analyses\figureMaking\code
Created Date: Saturday October 7th 2023
Author: gjowl
-----
Last Modified: Saturday October 7th 2023 7:48:19 pm
Modified By: gjowl
-----
Description:
Replaces the interface of the data file with the interface of the interface file. Since the interface is a number,
there are some times where I forgot to read it in as a string. So I need to go back to the file that has the 
original interface and replace the new file's interface column with the old file's interface column.
-----
'''

import os, sys, pandas as pd

# read the command line arguments
interfaceFile = sys.argv[1]
dataFile = sys.argv[2]
outputFile = sys.argv[3]
outputDir = sys.argv[4]

os.makedirs(name=outputDir, exist_ok=True)

# read the input file and the file to merge as dataframes
df = pd.read_csv(dataFile, sep=',', dtype={'Interface': str})
interfaceDf = pd.read_csv(interfaceFile, sep=',', dtype={'Interface': str})

# replace the interface column with the interfaceDf interface column for matching sequences
for i in range(0, len(df)):
    # get the sequence
    sequence = df['Directory'][i]
    # get the interface
    interface = interfaceDf[interfaceDf['Sequence'] == sequence]['Interface']
    # if the interface is not empty
    if len(interface) > 0:
        # replace the interface
        df['Interface'][i] = interface.values[0]

# output the dataframe to a csv file without the index
df.to_csv(f'{outputDir}/{outputFile}.csv', index=False)