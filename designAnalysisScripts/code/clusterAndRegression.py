import os, sys, pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn import preprocessing, svm
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression as lr
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
import seaborn as sns

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

def kmeanCluster(df, cols, n_clusters, outputDir):
    # create scaled dataframe for clustering
    scaled_df = MinMaxScaler().fit_transform(df[cols])

    km = KMeans(n_clusters=n_clusters, n_init=1000)
    y_pred = km.fit_predict(df[cols])
    print(y_pred)

    print(km.cluster_centers_)

    df['cluster'] = km.labels_
    sns.scatterplot(x='endXShift', y='endCrossingAngle', data=df, hue='cluster')
    plt.savefig(f'{outputDir}/clustered.png')

    # output the dataframes to csv
    df.to_csv(f'{outputDir}/clusteredData.csv', index=False)
    # reset the plot
    plt.clf()

# read in a dataframe from the command line
df = pd.read_csv(sys.argv[1], dtype={'Interface': str})
outputDir = sys.argv[2]

# keep only data where total < -5
df = df[df['Total'] < -5]

# columns of data to be used for clustering
cols = ['endXShift', 'endCrossingAngle', 'endAxialRotation', 'endZShift']

n_clusters = 3
# loop through the unique regions
for region in df['Region'].unique():
    # get the data for the region
    regionData = df[df['Region'] == region]
    # define the output directory for the region
    regionDir = f'{outputDir}/{region}'
    # make the output directory if it doesn't exist
    os.makedirs(name=regionDir, exist_ok=True)
    kmeanCluster(regionData, cols, n_clusters, regionDir)
    # loop through the unique clusters
    for cluster in regionData['cluster'].unique():
        # get the data for the cluster
        clusterData = regionData[regionData['cluster'] == cluster]
        # define the output directory for the cluster 
        clusterDir = f'{regionDir}/{cluster}'
        # make the output directory if it doesn't exist
        os.makedirs(name=clusterDir, exist_ok=True)
        # plot the data
        plotLinearRegression(clusterData, clusterDir, 'endXShift', 'endCrossingAngle')
        plotLinearRegression(clusterData, clusterDir, 'endXShift', 'endAxialRotation')
        plotLinearRegression(clusterData, clusterDir, 'endXShift', 'endZShift')
        plotLinearRegression(clusterData, clusterDir, 'endCrossingAngle', 'endAxialRotation')
        plotLinearRegression(clusterData, clusterDir, 'endCrossingAngle', 'endZShift')
        plotLinearRegression(clusterData, clusterDir, 'endAxialRotation', 'endZShift')
        plotLinearRegression(clusterData, clusterDir, 'Total', 'VDWDiff')
        plotLinearRegression(clusterData, clusterDir, 'Total', 'HBONDDiff')
        plotLinearRegression(clusterData, clusterDir, 'Total', 'IMM1Diff')
        plotLinearRegression(clusterData, clusterDir, 'Total', 'endXShift')
        plotLinearRegression(clusterData, clusterDir, 'Total', 'endCrossingAngle')
        plotLinearRegression(clusterData, clusterDir, 'Total', 'endAxialRotation')
        plotLinearRegression(clusterData, clusterDir, 'Total', 'endZShift')

