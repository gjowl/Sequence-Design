import os, sys, random, pandas as pd
import numpy as np, seaborn as sns
import matplotlib.pyplot as plt
from kneed import KneeLocator
from sklearn import preprocessing, svm
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression as lr
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import silhouette_score
from clusterStructureByGeometry import kmeanCluster, getClusterNumber
from linearRegressionAnalysis import plotLinearRegression

if __name__ == "__main__":
    # read in a dataframe from the command line
    df = pd.read_csv(sys.argv[1], dtype={'Interface': str})
    output_dir = sys.argv[2]
    
    # keep only data where total < -5
    df = df[df['Total'] < -5]
    
    # columns of data to be used for clustering
    #cols = ['endXShift', 'endCrossingAngle', 'endAxialRotation', 'endZShift', 'Total']
    cols = ['endXShift', 'endCrossingAngle', 'Total']
    cluster_cols = ['endXShift', 'endCrossingAngle', 'endAxialRotation', 'endZShift', 'VDWDiff', 'HBONDDiff', 'IMM1Diff', 'Total']
    n_clusters = 3
    
    # loop through the unique regions to cluster and plot linear regressions for each cluster in each region
    for region in df['Region'].unique():
        # get the data for the region
        region_data = df[df['Region'] == region]
        # define the output directory for the region
        region_dir = f'{output_dir}/{region}'
        # make the output directory if it doesn't exist
        os.makedirs(name=region_dir, exist_ok=True)
        n_clusters = getClusterNumber(region_data, region_dir)
        region_data = kmeanCluster(region_data, cols, n_clusters, region_dir)
        # loop through the unique clusters
        for cluster in region_data['cluster'].unique():
            # get the data for the cluster
            cluster_data = region_data[region_data['cluster'] == cluster]
            # define the output directory for the cluster 
            cluster_dir = f'{region_dir}/Cluster_{cluster}'
            # make the output directory if it doesn't exist
            os.makedirs(name=cluster_dir, exist_ok=True)
            # loop through the columns and plot the linear regression
            for i in range(len(cluster_cols)):
                for j in range(i+1, len(cluster_cols)):
                    plotLinearRegression(cluster_data, cluster_dir, cluster_cols[i], cluster_cols[j])