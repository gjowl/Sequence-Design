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
from kmeansCluster import getClusterNumber

"""
This pipeline takes in a dataframe, preproccesses it, and clusters it using k-means clustering.
"""

# the below analyzes the data to get the best number of components to cluster with
def getBestComponentNumber(pipe, cluster_data, true_labels, max_components):
    # Empty lists to hold evaluation metrics
    silhouette_scores, ari_scores = [], []
    for n in range(2, max_components):
        # This set the number of components for pca
        pipe["preprocessor"]["pca"].n_components = n
        pipe.fit(cluster_data)
   
        # calculate the silhouette score and ari score
        silhouette_coef = silhouette_score(
            pipe["preprocessor"].transform(cluster_data),
            pipe["clusterer"]["kmeans"].labels_,
        )
        ari = adjusted_rand_score(
            true_labels,
            pipe["clusterer"]["kmeans"].labels_,
        )
   
        # Add metrics to their lists
        silhouette_scores.append(silhouette_coef)
        ari_scores.append(ari)

    # get the best number of components by finding the max of the ari scores
    n_components = np.argmax(ari_scores) + 2
    print(f'Best number of components: {n_components}')

    # Plot the evaluation metrics
    plt.figure(figsize=(8, 8))
    plt.plot(range(2, max_components), silhouette_scores, c="#008fd5", label="Silhouette Coefficient")
    plt.plot(range(2, max_components), ari_scores, c="#fc4f30", label="ARI")
   
    plt.xlabel("n_components")
    plt.legend()
    plt.title(f'Clustering Performance as a Function of {max_components} components')
    plt.tight_layout()

    # save the plot
    plt.savefig(f'{output_dir}/getBestCluster.png')
    plt.clf()
    return n_components

if __name__ == "__main__":
    # read in a dataframe from the command line
    df = pd.read_csv(sys.argv[1], dtype={'Interface': str})
    output_dir = sys.argv[2]

    # make the output directory if it doesn't exist
    os.makedirs(name=output_dir, exist_ok=True)

    # keep only data where total < -5
    df = df[df['Total'] < -5]

    # columns of data to be used for clustering
    cols = ['endXShift', 'endCrossingAngle', 'endAxialRotation', 'endZShift', 'VDWDiff', 'HBONDDiff', 'IMM1Diff', 'Total']

    # get the best number of clusters
    n_clusters = getClusterNumber(df, cols, output_dir)

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
    
    # get the true labels (in this case with all the data, the region)
    label_encoder = LabelEncoder()
    true_labels = label_encoder.fit_transform(df['Region'].values)

    # TODO: right here I think I need to somehow get the cluster number to go with the actual data somehow

    # get the best number of components to cluster with
    n_components = getBestComponentNumber(pipe, cluster_data, true_labels, len(cols))

    # fit the pipeline to the data (executes the preproccessor and clusterer on the data)
    pipe["preprocessor"]["pca"].n_components = n_components
    pipe.fit(cluster_data)

    preproccessed_data = pipe['preprocessor'].transform(cluster_data)

    # get the cluster labels
    cluster_labels = pipe['clusterer']['kmeans'].labels_

    # output the silhouette score
    print(f'Silhouette Score: {silhouette_score(preproccessed_data, cluster_labels)}')

    # output the adjusted rand score
    print(f'Adjusted Rand Score: {adjusted_rand_score(true_labels, cluster_labels)}')

    # make the pca columns list
    pca_cols = []
    for i in range(n_components):
        pca_cols.append(f'component_{i+1}')
    
    # plot the data with the cluster labels
    pcadf = pd.DataFrame(
        pipe["preprocessor"].transform(cluster_data),
        columns=pca_cols
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