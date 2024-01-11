# @Author: Gilbert Loiseau
# @Date:   2021-10-22
# @Filename: pcaPlotter.py
# @Last modified by:   Gilbert Loiseau
# @Last modified time: 2021-11-28



import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import plotly
import plotly.express as px
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

#FUNCTIONS
#def getCountsPerDensityArrays(df1, df2, numberBins, binSize):
#    bins = np.array([])
#    density = np.array([])
#    binCount1 = np.array([])
#    binCount2 = np.array([])
#
#    i=1
#    while i<numberBins:
#        currDensity = i*binSize
#        tmpdf1 = df1[df1["angleDistDensity"] < currDensity]
#        tmpdf2 = df2[df2["angleDistDensity"] < currDensity]
#        bins = np.append(bins, currDensity-binSize)
#        density = np.append(density, currDensity)
#        binCount1 = np.append(binCount1, tmpdf1.shape[0])
#        binCount2 = np.append(binCount2, tmpdf2.shape[0])
#        print(tmpdf1)
#        i+=1
#    return bins, density, binCount1, binCount2
#
#def addArraysToDataframe(bins, density, binCount1, binCount2):
#    df = pd.DataFrame()
#    df["Bins"] = bins
#    df["Density"] = density
#    df["Count1"] = binCount1
#    df["Count2"] = binCount2
#    return df
#
#def plotHistograms(df):
#    # Plotting code below
#    fig, ax = plt.subplots()
#    plt.xlabel('Density')
#    plt.ylabel('Count')
#    plt.title('Count by density')
#    plt.bar(df['Count1'], df['Density'])
#    plt.show()
#    plt.bar(df['Density'], df['Count2'])
#    plt.show()

#Main code
geometries = "C:\\Users\\gjowl\\Documents\\2021_10_21_allGeometryKde.csv"

# Gets the header line to be used for the analysis
#pcaFeatures = pd.read_csv(geometries, nrows=0).columns.tolist()
pcaFeatures = ['xShift', 'crossingAngle', 'Z1', 'Z2', 'Rot1', 'Rot2']
df = pd.read_csv(geometries, sep=",")

#helperDf = pd.DataFrame()
#
#numberBins = 6
#binSize = 0.20
#bins = np.array([])
#density = np.array([])
#binCountCho = np.array([])
#binCountGen = np.array([])
#
#bins, density, binCountCho, binCountGen = getCountsPerDensityArrays(dfChosen, dfGenerated, numberBins, binSize)
#helperDf = addArraysToDataframe(bins, density, binCountCho, binCountGen)
#
#labels = helperDf.Bins.values
#
#print(dfChosen)
#x = df.loc[:, pcaFeatures].values
import plotly.io as pio
pio.renderers.default='browser'
#from sklearn.datasets import load_boston
#
#boston = load_boston()
#df = pd.DataFrame(boston.data, columns=boston.feature_names)
#n_components = 4
#
#pca = PCA(n_components=n_components)
#components = pca.fit_transform(df)
#
#total_var = pca.explained_variance_ratio_.sum() * 100
#
#labels = {str(i): f"PC {i+1}" for i in range(n_components)}
#labels['color'] = 'Median Price'
#
##fig, ax = plt.subplots()
#fig = px.scatter_matrix(
#    components,
#    color=boston.target,
#    dimensions=range(n_components),
#    labels=labels,
#    title=f'Total Explained Variance: {total_var:.2f}%',
#)
#fig.update_traces(diagonal_visible=False)
#fig.show()

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

#percent_variance = np.round(pca.explained_variance_ratio_* 100, decimals =2)
#columns = ['PC1', 'PC2', 'PC3', 'PC4','PC5','PC6']
#plt.bar(x= range(1,7), height=percent_variance, tick_label=columns)
#plt.ylabel('Percentate of Variance Explained')
#plt.xlabel('Principal Component')
#plt.title('PCA Scree Plot')
#plt.show()

#plt.scatter(pcaDf.PC1, pcaDf.PC2)
#plt.title('PC1 against PC2')
#plt.xlabel('PC1')
#plt.ylabel('PC2')

X_st =  StandardScaler().fit_transform(x)
pca_out = PCA().fit(X_st)

loadings = pca_out.components_

pca_scores = PCA().fit_transform(X_st)
cluster.biplot(cscore=pca_scores, loadings=loadings, labels=X.columns.values, var1=round(pca_out.explained_variance_ratio_[0]*100, 2),
    var2=round(pca_out.explained_variance_ratio_[1]*100, 2), colorlist=target)