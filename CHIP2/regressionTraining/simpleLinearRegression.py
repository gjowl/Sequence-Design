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

    # the below I got from: https://www.geeksforgeeks.org/python-linear-regression-using-sklearn/#
    X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.25, random_state=0)

    regr = LinearRegression()

    regr.fit(X_train, y_train)
    print(regr.score(X_test, y_test))

    y_pred = regr.predict(X_test)
    plt.scatter(X_test, y_test, color='black')
    plt.plot(X_test, y_pred, color='blue', linewidth=3)

    # TODO: I also have a script from a year ago in clusterAnalysis/code/linearRegression.py; could look at that for more detail and can't remember if it worked?
    # that same directory also has some clustering code, and now with actual experimental data, could be used to cluster for meaningful data?