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

    # split the data into training and testing
    X_train, X_test, y_train, y_test = train_test_split(x, y, test_size = 0.25)

    # fit the linear regression model
    regr = lr()
    regr.fit(X_train, y_train)
    regression_score = regr.score(X_test, y_test)

    # check the regression score
    if regression_score < 0.3:
        return
    # if the regression score is good, plot the data and output
    else:
        # plot the data for the regression
        y_pred = regr.predict(X_test)
        plt.scatter(X_test, y_test, color ='lightskyblue')
        plt.plot(X_test, y_pred, color ='k')

        # putting labels for x-axis and y-axis
        plt.xlabel(xAxis)
        plt.ylabel(yAxis)

        # title of the plot
        plt.title(f'{xAxis} vs {yAxis}')

        # show the correlation on the top left of the plot
        plt.text(0.05, 1.10, f'R^2 = {regression_score:.2f}', horizontalalignment='left', verticalalignment='top', transform=plt.gca().transAxes)
        # output the cluster number on the top right of the plot
        cluster = df['cluster'].unique()[0]
        plt.text(0.95, 1.10, f'Cluster {cluster}', horizontalalignment='right', verticalalignment='top', transform=plt.gca().transAxes)
        # output the number of data points on the top right of the plot
        plt.text(0.95, 1.05, f'N = {len(df)}', horizontalalignment='right', verticalalignment='top', transform=plt.gca().transAxes)

        # save the plot
        plt.savefig(f'{outputDir}/{xAxis}_vs_{yAxis}.png')
        # reset the plot
        plt.clf()

if __name__ == "__main__":
    """
    This script will read in a csv file from the command line and output linear regression plots for each cluster in each region
    """
    # read in the data from command line
    data = sys.argv[1]
    outputDir = sys.argv[2]

    # make the output directory if it doesn't exist
    os.makedirs(name='outputDir', exist_ok=True)

    # read in the data to a dataframe
    df = pd.read_csv(data)

    # define the columns to be used for the linear regression
    cols = ['endXShift', 'endCrossingAngle', 'endAxialRotation', 'endZShift', 'VDWDiff', 'HBONDDiff', 'IMM1Diff', 'Total']

    # loop through the unique clusters
    for cluster in df['cluster'].unique():
        # get the data for the cluster
        clusterData = df[df['cluster'] == cluster]
        # loop through the columns and plot the linear regression
        for i in range(len(cols)):
            for j in range(i+1, len(cols)):
                plotLinearRegression(clusterData, outputDir, cols[i], cols[j])