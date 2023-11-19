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
This pipeline takes in a dataframe, preproccesses it using pca, and clusters it using k-means clustering.
It outputs the pca results as a dataframe, cluster information as a png, and the input data with the cluster numbers as a csv.
"""
# the below gets the most important components of the data (pca clusters on the top n_components)
def getMostImportantComponents(pipe, cols, n_components, output_dir):
    # get the index of the most important feature on EACH component
    # LIST COMPREHENSION HERE
    n_components = pipe['preprocessor']['pca'].components_.shape[0]
    most_important = [np.abs(pipe['preprocessor']['pca'].components_[i]).argmax() for i in range(n_components)]
    
    initial_feature_names = cols
    # get the names
    most_important_names = [initial_feature_names[most_important[i]] for i in range(n_components)]

    # LIST COMPREHENSION HERE AGAIN
    dic = {'PC{}'.format(i): most_important_names[i] for i in range(n_components)}

    # build the dataframe
    df = pd.DataFrame(dic.items())
    # output the dataframe
    df.to_csv(f'{output_dir}/most_important_features.csv', index=False, header=False)

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
    plt.title(f'Clustering Performance as a Function of number of components')
    plt.tight_layout()

    # save the plot
    plt.savefig(f'{output_dir}/cluster_components.png')
    plt.clf()
    return n_components

if __name__ == "__main__":
    # get the input file from the command line
    input_file = sys.argv[1]

    # get the input file name without the extension and the path
    input_file_name = os.path.splitext(input_file)[0]
    input_file_name = os.path.basename(input_file_name)

    # read in a dataframe from the command line
    df = pd.read_csv(input_file, dtype={'Interface': str})
    output_dir = sys.argv[2]

    # make the output directory if it doesn't exist
    os.makedirs(name=output_dir, exist_ok=True)

    # keep only data where total < -5
    df = df[df['Total'] < -5]

    # create energy groups based on the total energy separated by 5
    df['energyGroup'] = pd.cut(df['Total'], bins=[-70, -40, -35, -30, -25, -20, -15, -10, -5], labels=['-40', '-35', '-30', '-25', '-20', '-15', '-10', '-5'])

    # columns of data to be used for clustering
    cols = sys.argv[3].split(',')

    for region in df['Region'].unique():
        # get the data for the region
        region_df = df[df['Region'] == region]

        # make the region directory if it doesn't exist
        region_dir = f'{output_dir}/{region}'
        os.makedirs(name=region_dir, exist_ok=True)

        # get the best number of clusters
        n_clusters = getClusterNumber(region_df, cols, region_dir)

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
        cluster_data = region_df[cols]
    
        # get the true labels (in this case with all the data, the region)
        label_encoder = LabelEncoder()
        true_labels = label_encoder.fit_transform(region_df['energyGroup'].values)

        # get the best number of components to cluster with
        n_components = getBestComponentNumber(pipe, cluster_data, true_labels, len(cols)+1)

        # fit the pipeline to the data (executes the preproccessor and clusterer on the data)
        pipe["preprocessor"]["pca"].n_components = n_components
        pipe.fit(cluster_data)
    
        # get the most important components used for clustering in order of importance
        getMostImportantComponents(pipe, cols, n_components, region_dir)

        # preproccess the data using a transform
        preproccessed_data = pipe['preprocessor'].transform(cluster_data)

        # get the cluster labels
        cluster_labels = pipe['clusterer']['kmeans'].labels_

        # output the silhouette score
        print(f'Silhouette Score: {silhouette_score(preproccessed_data, cluster_labels)}')

        # output the adjusted rand score
        print(f'Adjusted Rand Score: {adjusted_rand_score(true_labels, cluster_labels)}')

        # save the sequences as labels for the data
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

        # save the sequences as labels for the data to extract the data for further analysis
        sequence_labels = label_encoder.fit_transform(region_df['Sequence'].values)
        pcadf["sequence"] = label_encoder.inverse_transform(sequence_labels)

        #plt.style.use("fivethirtyeight")
        plt.figure(figsize=(12, 12))
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
        plt.savefig(f'{region_dir}/cluster.png', bbox_inches='tight')

        # output the data with the cluster labels
        pcadf.to_csv(f'{region_dir}/clustered_data.csv')

        # add the cluster column to the input dataframe with all of the data (I think the data is transformed in the same order, so don't need to make this complicated)
        region_df['cluster'] = pcadf['predicted_cluster']

        # output the dataframe
        region_df.to_csv(f'{region_dir}/{input_file_name}_clusters.csv')