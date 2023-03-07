import os, sys, pandas as pd

"""
This file loops through a datafile of design runs and the initial geometry file and outputs a csv file 
for each region (gas, left, right) with the successful design runs from that region.
"""

# get the current directory
currentDir = os.getcwd()

# get the data file from the command line
dataFile = sys.argv[1]
geomFile = sys.argv[2]
outputDir = sys.argv[3]

# make the output directory if it doesn't exist
os.makedirs(outputDir, exist_ok=True)

# open the data file with interface as string
data = pd.read_csv(dataFile, dtype={'Interface':str})
geom = pd.read_csv(geomFile, dtype={'interface':str, 'runNumber':str}, header=0)

# define the runNumber column, splitting by the '_' in the Directory column
data['runNumber'] = data['Directory'].str.split('_').str[1]

# loop through dataframe rows and break down into regions
for index, row in data.iterrows():
    # check the xShift value
    if row['startXShift'] <= 7.5:
        # add region column GAS
        data.loc[index, 'Region'] = 'gas'
    elif row['startXShift'] > 7.5 and row['startCrossingAngle'] < 0:
        # add region column GAS
        data.loc[index, 'Region'] = 'right'
    elif row['startXShift'] > 7.5 and row['startCrossingAngle'] > 0:
        # add region column Left
        data.loc[index, 'Region'] = 'left'

for region in data['Region'].unique():
    # get the data for the region
    regionData = data[data['Region'] == region]
    # keep the rows in the geom dataframe that are in the regionData dataframe
    regionGeom = geom[geom['runNumber'].isin(regionData['runNumber'])]
    # output the regionData to a csv file with interface as a string
    regionGeom.to_csv(f'{outputDir}/{region}_rerun.csv', index=False)