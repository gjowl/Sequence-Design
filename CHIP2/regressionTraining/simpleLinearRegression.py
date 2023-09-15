import os, sys, numpy as np, pandas as pd
from sklearn.linear_model import LinearRegression

# read in command line arguments
dataFile = sys.argv[1]
outputDir = sys.argv[2]

# read in the data file
df = pd.read_csv(dataFile)

# hardcoded: choose which columns to use for the regression
xAxis = 'Percent GpA'
yAxis = 'Total'

# loop through the design types
for design in df['Sample'].unique():
    input_df = df[df['Sample'] == design]
    # get the x and y values
    x = input_df[xAxis].values.reshape(-1,1)
    y = input_df[yAxis].values.reshape(-1,1)
    # TODO: below train the model on the x and y axis
    model = LinearRegression().fit(x, y)


