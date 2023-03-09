import os, sys
import numpy as np 
import pandas as pd
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler
from matplotlib import pyplot as plt

# from: https://machinelearningknowledge.ai/tutorial-for-k-means-clustering-in-python-sklearn/#:~:text=Example%20of%20K%20Means%20Clustering%20in%20Python%20Sklearn,on%20their%20Age%2C%20Annual%20Income%2C%20Spending%20Score%2C%20etc.

# read in the data from command line
data = sys.argv[1]
outputDir = sys.argv[2]

# make the output directory if it doesn't exist
os.makedirs(name=f'{outputDir}', exist_ok=True)

# read in the data to a dataframe with interface as string
df = pd.read_csv(data, dtype={'Interface': str})

# columns of data to be used for clustering
cols = ['endXShift', 'endCrossingAngle', 'endAxialRotation', 'endZShift']
df = df[cols]

# create scaled dataframe for clustering
scaled_df = MinMaxScaler().fit_transform(df[['endXShift', 'endCrossingAngle', 'endAxialRotation', 'endZShift']])

km = KMeans(n_clusters=6)
y_pred = km.fit_predict(df[['endXShift', 'endCrossingAngle', 'endAxialRotation', 'endZShift']])
print(y_pred)

print(km.cluster_centers_)

df['cluster'] = km.labels_
sns.scatterplot(x='endXShift', y='endCrossingAngle', data=df, hue='cluster')
plt.savefig(f'{outputDir}/clustered.png')