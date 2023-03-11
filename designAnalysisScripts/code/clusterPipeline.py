import os, sys
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score, adjusted_rand_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, MinMaxScaler

"""
This pipeline takes in a dataframe, preproccesses it, and clusters it using k-means clustering.
"""

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

# TODO: figure out how to decrease the dimensions of the data before clustering; how many components and which ones
    # implement PCA to reduce the number of dimensions
    preproccessor = Pipeline([
        ('scaler', MinMaxScaler()),
        ('pca', PCA(n_components=2))
    ])

    # implement k-means clustering into a pipeline
    clusterer = Pipeline([
        ('kmeans', KMeans(n_clusters=n_clusters,
                          init='k-means++',
                          n_init=10,
                          max_iter=300,
                          random_state=42,
                          )
        )
    ])

    # combine the preproccessor and clusterer into a single pipeline
    pipe = Pipeline([
        ('preprocessor', preproccessor),
        ('clusterer', clusterer)
    ])

    # fit the pipeline to the data (executes the preproccessor and clusterer on the data)
    cluster_data = df[cols]
    pipe.fit(cluster_data)

    preproccessed_data = pipe['preprocessor'].transform(cluster_data)

    # get the cluster labels
    cluster_labels = pipe['clusterer']['kmeans'].labels_

    # output the silhouette score
    print(f'Silhouette Score: {silhouette_score(preproccessed_data, cluster_labels)}')

    # get the true labels (in this case with all the data, the region)
    label_encoder = LabelEncoder()
    true_labels = label_encoder.fit_transform(df['Region'].values)

    # output the adjusted rand score
    print(f'Adjusted Rand Score: {adjusted_rand_score(true_labels, cluster_labels)}')

    # plot the data with the cluster labels
    pcadf = pd.DataFrame(
        pipe["preprocessor"].transform(cluster_data),
        columns=["component_1", "component_2"],
    )
    
    pcadf["predicted_cluster"] = pipe["clusterer"]["kmeans"].labels_
    pcadf["true_label"] = label_encoder.inverse_transform(true_labels)

    #plt.style.use("fivethirtyeight")
    plt.figure(figsize=(8, 8))
    
    scat = sns.scatterplot(
        x = "component_1",
        y = "component_2",
        s=50,
        data=pcadf,
        hue="predicted_cluster",
        style="true_label",
        palette="Set2",
    )
    
    scat.set_title(
        "Clustering results from all design data by geometry"
    )
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.0)
    
    # save the plot
    plt.savefig(f'{output_dir}/cluster.png')

    # output the data with the cluster labels
    pcadf.to_csv(f'{output_dir}/clustered_data.csv')