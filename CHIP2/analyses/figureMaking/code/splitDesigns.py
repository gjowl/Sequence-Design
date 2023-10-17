'''
File: d:\github\Sequence-Design\CHIP2\analyses\figureMaking\code\splitDesigns.py
Project: d:\github\Sequence-Design\CHIP2\analyses\figureMaking\code
Created Date: Monday October 16th 2023
Author: gjowl
-----
Last Modified: Monday October 16th 2023 7:55:49 pm
Modified By: gjowl
-----
Description:
Splits designs by their design type (ala or leu).
-----
'''

import os, sys, pandas as pd

# read the command line arguments
inputFile = sys.argv[1]
outputFile = sys.argv[2]
outputDir = sys.argv[3]

os.makedirs(name=outputDir, exist_ok=True)

# read the input file as a dataframe
df = pd.read_csv(inputFile, sep=',', dtype={'Interface': str})

# separate into the two different designs
df_ala = df[df['Design'] == 'ala']
df_leu = df[df['Design'] == 'leu']

# output the dataframe to a csv file without the index
df_ala.to_csv(f'{outputDir}/{outputFile}_ala.csv', index=False)
df_leu.to_csv(f'{outputDir}/{outputFile}_leu.csv', index=False)