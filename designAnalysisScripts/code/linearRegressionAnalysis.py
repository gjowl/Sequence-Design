import os, sys, pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn import preprocessing, svm
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression as lr

# functions
def plotLinearRegression(df, outputDir, xAxis, yAxis):
    x = np.array(df[xAxis].values.reshape(-1,1))
    y = np.array(df[yAxis].values.reshape(-1,1))

    X_train, X_test, y_train, y_test = train_test_split(x, y, test_size = 0.25)

    regr = lr()
    regr.fit(X_train, y_train)
    print(xAxis, yAxis, regr.score(X_test, y_test))

    # plot the data
    y_pred = regr.predict(X_test)
    plt.scatter(X_test, y_test, color ='b')
    plt.plot(X_test, y_pred, color ='k')

    # putting labels for x-axis and y-axis
    plt.xlabel(xAxis)
    plt.ylabel(yAxis)

    # save the plot
    plt.savefig(f'{outputDir}/{xAxis}_vs_{yAxis}.png')
    # reset the plot
    plt.clf()

# read in the data from command line
data = sys.argv[1]
outputDir = sys.argv[2]

# make the output directory if it doesn't exist
os.makedirs(name='outputDir', exist_ok=True)

# read in the data to a dataframe
df = pd.read_csv(data)

# loop through the unique clusters
for cluster in df['cluster'].unique():
    # get the data for the cluster
    clusterData = df[df['cluster'] == cluster]

    # plot the data
    plotLinearRegression(clusterData, outputDir, 'endXShift', 'endCrossingAngle')
    plotLinearRegression(clusterData, outputDir, 'endXShift', 'endAxialRotation')
    plotLinearRegression(clusterData, outputDir, 'endXShift', 'endZShift')
    plotLinearRegression(clusterData, outputDir, 'endCrossingAngle', 'endAxialRotation')
    plotLinearRegression(clusterData, outputDir, 'endCrossingAngle', 'endZShift')
    plotLinearRegression(clusterData, outputDir, 'endAxialRotation', 'endZShift')
    plotLinearRegression(clusterData, outputDir, 'Total', 'VDWDiff')
    plotLinearRegression(clusterData, outputDir, 'Total', 'HBONDDiff')
    plotLinearRegression(clusterData, outputDir, 'Total', 'IMM1Diff')
    plotLinearRegression(clusterData, outputDir, 'Total', 'endXShift')
    plotLinearRegression(clusterData, outputDir, 'Total', 'endCrossingAngle')
    plotLinearRegression(clusterData, outputDir, 'Total', 'endAxialRotation')
    plotLinearRegression(clusterData, outputDir, 'Total', 'endZShift')
    exit(0)
