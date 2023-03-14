import os, sys, random, pandas as pd
import numpy as np, seaborn as sns 
from matplotlib import pyplot as plt
from kneed import KneeLocator
from sklearn import preprocessing, svm
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression as lr
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import silhouette_score

# from: https://machinelearningknowledge.ai/tutorial-for-k-means-clustering-in-python-sklearn/#:~:text=Example%20of%20K%20Means%20Clustering%20in%20Python%20Sklearn,on%20their%20Age%2C%20Annual%20Income%2C%20Spending%20Score%2C%20etc.

# functions
# elbow method to find the optimal number of clusters
# sse decreases as the number of clusters increases
# as more centroids are added, the distance from points to centroids decreases
# finding the "elbow" of the curve is a reasonable trade-off between error and number of clusters
def elbowMethod(scaled_df, kmeans_kwargs, outputDir):
    # A list holds the SSE values for each k
    sse = []
    for k in range(1, 11):
        kmeans = KMeans(n_clusters=k, **kmeans_kwargs)
        kmeans.fit(scaled_df)
        sse.append(kmeans.inertia_)
    #plt.style.use("fivethirtyeight")
    plt.plot(range(1, 11), sse)
    plt.xticks(range(1, 11))
    plt.xlabel("Number of Clusters")
    plt.ylabel("SSE")
    plt.savefig(f'{outputDir}/elbow.png')
    plt.clf()
    # find the elbow point for the optimal number of clusters
    k1 = KneeLocator(range(1, 11), sse, curve="convex", direction="decreasing")
    n_clusters = k1.elbow
    return n_clusters

# silhouette method to find the optimal number of clusters
# quantifies how well a data point fits into its assigned cluster based on two factors:
#  - how close the data point is to other points in the cluster
#  - how far away the data point is from points in the neighboring clusters
# larger numbers indicate that the data point is better matched to its cluster and worse matched to neighboring clusters
def silhouetteMethod(scaled_df, kmeans_kwargs, outputDir):
    # A list holds the silhouette coefficients for each k
    silhouette_coefficients = []
    # Notice you start at 2 clusters for silhouette coefficient
    for k in range(2, 11):
        kmeans = KMeans(n_clusters=k, **kmeans_kwargs)
        kmeans.fit(scaled_df)
        score = silhouette_score(scaled_df, kmeans.labels_)
        silhouette_coefficients.append(score)
    #plt.style.use("fivethirtyeight")
    plt.plot(range(2, 11), silhouette_coefficients)
    plt.xticks(range(2, 11))
    plt.xlabel("Number of Clusters")
    plt.ylabel("Silhouette Coefficient")
    plt.savefig(f'{outputDir}/silhouette.png')
    plt.clf()

    # get the index of the highest silhouette coefficient from the list
    n_clusters = silhouette_coefficients.index(max(silhouette_coefficients)) + 2
    return n_clusters

#https://realpython.com/k-means-clustering-python/#:~:text=The%20standard%20version%20of%20the%20k-means%20algorithm%20is,two%20runs%20can%20converge%20on%20different%20cluster%20assignments.
def getClusterNumber(df, cols, outputDir):
    # create scaled dataframe for clustering
    scaled_df = MinMaxScaler().fit_transform(df[cols])

    # setup kmeans parameters for elbow and silhouette methods
    kmeans_kwargs = {
        "init": "random",
        "n_init": 10,
        "max_iter": 300,
        "random_state": 42,
    }

    # call elbow and silhouette methods to find the optimal number of clusters
    elbow_n_clusters = elbowMethod(scaled_df, kmeans_kwargs, outputDir)
    print(f'elbow: {elbow_n_clusters}')
    sil_n_clusters = silhouetteMethod(scaled_df, kmeans_kwargs, outputDir)
    print(f'silhouette: {sil_n_clusters}')
    # if the two methods agree on the number of clusters, use that number
    if elbow_n_clusters == sil_n_clusters:
        n_clusters = elbow_n_clusters
    else:
        # pick the higher number of clusters
        n_clusters = max(elbow_n_clusters, sil_n_clusters)
    return n_clusters

def kmeanCluster(df, cols, n_clusters, outputDir):
    # create scaled dataframe for clustering
    scaled_df = MinMaxScaler().fit_transform(df[cols])
    
    # cluster the data; default n_init is 1000 cluster runs
    km = KMeans(n_clusters=n_clusters, n_init=1000)
    y_pred = km.fit_predict(df[cols])
    #print(km.cluster_centers_)

    # add the cluster number to the dataframe
    df['cluster'] = km.labels_
    sns.scatterplot(x='endXShift', y='endCrossingAngle', data=df, hue='cluster')
    plt.savefig(f'{outputDir}/clustered.png')

    # output the dataframes to csv
    df.to_csv(f'{outputDir}/clusteredData.csv', index=False)
    # reset the plot
    plt.clf()
    return df

"""
This script takes in a csv file with the following columns: endXShift, endCrossingAngle, endAxialRotation, endZShift
and outputs a csv file with the k-means cluster number for each data point.
"""
if __name__ == "__main__":
    # read in the data from command line
    data = sys.argv[1]
    outputDir = sys.argv[2]

    # make the output directory if it doesn't exist
    os.makedirs(name=f'{outputDir}', exist_ok=True)

    # read in the data to a dataframe with interface as string
    df = pd.read_csv(data, dtype={'Interface': str})

    # keep only data where total < -5
    df = df[df['Total'] < -5]

    # columns of data to be used for clustering
    cols = ['endXShift', 'endCrossingAngle', 'endAxialRotation', 'endZShift']

    n_clusters = getClusterNumber(df, cols, outputDir)
    kmeanCluster(df, cols, n_clusters, outputDir)
