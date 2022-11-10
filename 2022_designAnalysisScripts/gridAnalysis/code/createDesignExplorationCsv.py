import sys
import pandas as pd

# Read in the data file
datafile = sys.argv[1]
data = pd.read_csv(datafile)

# get the directory from the datafile
directory = datafile[:datafile.rfind('/')+1]

# get column names of dataframe
cols = data.columns

# find matching values in the Region column
gxxxgData = data[data['Region'] == 'GASright']
right = data[data['Region'] == 'Right']
left = data[data['Region'] == 'Left'] 

# add all dataframes to a list
dataframes = [gxxxgData, right, left]

cols = 'seed,xShift,crossingAngle,negAngle,axialRotation,zShift'.split(',')

# loop through values for each column in the dataframe
outputDf = pd.DataFrame()
for df in dataframes:
    i = 0
    for xShift in df['xShift']:
        # loop through values within next column
        for crossingAngle in df['crossingAngle']:
            # check crossingAngle positive or negative
            negAngle = 'false'
            if crossingAngle < 0:
                negAngle = 'true'
                # make crossingAngle positive
                crossingAngle = -crossingAngle
            # loop through values within next column
            for axialRotation in df['axialRotation']:
                # loop through values within next column
                for zShift in df['zShift']:
                   # add all values to a new row of the output dataframe using concat
                    outputDf = pd.concat([outputDf, pd.DataFrame([[i,xShift, crossingAngle, negAngle, axialRotation, zShift]], columns=cols)])
                    i += 1
                            
# print outputDf to a csv file in the same directory as the original data file with no first column
outputDf.to_csv(directory + 'designExploration.csv', index=False)

