import os, sys, pandas as pd

# get the input data file from command line
dataFile = sys.argv[1]

# get the output directory from the data file
outputDir = os.getcwd()

# read in the data file
df = pd.read_csv(dataFile)

# loop through dataframe rows and break down into regions
for index, row in df.iterrows():
    # check the xShift value
    if row['endXShift'] <= 7.5:
        # add region column GAS
        df.loc[index, 'Region'] = 'GAS'
    elif row['endXShift'] > 7.5 and row['endCrossingAngle'] < 0:
        # add region column GAS
        df.loc[index, 'Region'] = 'Right'
    elif row['endXShift'] > 7.5 and row['endCrossingAngle'] > 0:
        # add region column Left
        df.loc[index, 'Region'] = 'Left'

# save the data to a csv file
df.to_csv(f'{outputDir}/allData.csv', index=False)
