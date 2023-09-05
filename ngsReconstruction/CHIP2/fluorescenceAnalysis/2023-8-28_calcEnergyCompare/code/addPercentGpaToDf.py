import os, sys, pandas as pd

"""
 This script will append the input datafile with the toxgreen data from another input datafile.
"""

# read in the data file
dataFile = sys.argv[1]
toxgreenFile = sys.argv[2]
outputFile = sys.argv[3]
outputDir = sys.argv[4]

# check if dataFile exists
if os.path.isfile(outputFile):
    # quit
    print('DataFile', outputFile,'exists. To overwrite, delete the file and run again.')
    sys.exit()

# read in the data files
df = pd.read_csv(dataFile)
toxgreenDf = pd.read_csv(toxgreenFile)

# get the columns of interest
toxgreenDf = toxgreenDf[['Sequence','PercentGpA','PercentStd','Sample','LB-12H_M9-36H']]

# define the sequence column for the datafile
df['Sequence'] = df['Geometry'].str[3:-5] # removes the first 3 and last 5 characters from the geometry column

# append the matching sequence data from the toxgreen datafile to the input datafile
df = df.merge(toxgreenDf, on='Sequence', how='left')

# output the dataframe to a csv file
df.to_csv(f'{outputDir}/{outputFile}.csv', sep=',', index=False)