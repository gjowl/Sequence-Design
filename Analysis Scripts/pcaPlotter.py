# @Author: Gilbert Loiseau
# @Date:   2021-10-22
# @Filename: pcaPlotter.py
# @Last modified by:   Gilbert Loiseau
# @Last modified time: 2022/03/17

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import plotly
import plotly.express as px
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

#Main code
geometries = "C:\\Users\\gjowl\\Documents\\2021_10_21_allGeometryKde.csv"

# Gets the header line to be used for the analysis
#pcaFeatures = pd.read_csv(geometries, nrows=0).columns.tolist()
pcaFeatures = ['xShift', 'crossingAngle', 'Z1', 'Z2', 'Rot1', 'Rot2']
df = pd.read_csv(geometries, sep=",")

import plotly.io as pio
pio.renderers.default='browser'

##x = StandardScaler().fit_transform(x)
x = df.iloc[:,:6]
n_components = 6
pca = PCA(n_components=n_components)
components = pca.fit_transform(x)
print(df.Kde)

total_var = pca.explained_variance_ratio_.sum() * 100

labels = {str(i): f"{pcaFeatures[i]}" for i in range(n_components)}
labels['color'] = 'Kde'

fig = px.scatter_matrix(
    components,
    color=df.Kde,
    dimensions=range(n_components),
    labels=labels,
    title=f'Total Explained Variance: {total_var:.2f}%',
)
fig.update_traces(diagonal_visible=False)
fig.show()

X_st =  StandardScaler().fit_transform(x)
pca_out = PCA().fit(X_st)

loadings = pca_out.components_

pca_scores = PCA().fit_transform(X_st)
cluster.biplot(cscore=pca_scores, loadings=loadings, labels=X.columns.values, var1=round(pca_out.explained_variance_ratio_[0]*100, 2),
    var2=round(pca_out.explained_variance_ratio_[1]*100, 2), colorlist=target)
