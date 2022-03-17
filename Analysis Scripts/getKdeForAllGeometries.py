"""
@author: gjowl
"""
"""
This file creates a kde file for pca analysis
"""
from datetime import date
from scipy import stats
from matplotlib import gridspec
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import re
import seaborn as sns

##############################################
#                 FUNCTIONS
##############################################
def calculateKde(paramValues, mins, maxs, cutoffs):
    tupleArray = np.array([])
    tmp=[()]
    for i in range(0,len(mins)):
        tmp.append((mins[i],maxs[i],cutoffs[i]))
    tmpTuple = tuple(tmp)
    tupleArray = np.asarray(tmpTuple)
    tupleArray = np.delete(tupleArray, 0)

    d1, d2 = np.mgrid[mins[0]:maxs[0]:cutoffs[0], mins[1]:maxs[1]:cutoffs[1]]
    d3, d4 = np.mgrid[mins[2]:maxs[2]:cutoffs[2], mins[3]:maxs[3]:cutoffs[3]]
    d5, d6 = np.mgrid[mins[4]:maxs[4]:cutoffs[4], mins[5]:maxs[5]:cutoffs[5]]

    X, Y = np.mgrid[0:6:20j, -100:100:20j]
    Z1, Z2 = np.mgrid[0:6:20j, 0:6:20j]
    R1, R2 = np.mgrid[0:100:20j, 0:100:20j]

    positions = np.vstack([d1.ravel(), d2.ravel(), d3.ravel(), d4.ravel(), d5.ravel(), d6.ravel()])
    values = np.vstack([paramValues[0], paramValues[1], paramValues[2], paramValues[3], paramValues[4], paramValues[5]])

    kernel = stats.gaussian_kde(values)
    kernel.set_bandwidth(bw_method='silverman')
    Z = np.reshape(kernel(positions).T,d1.shape)
    return positions, kernel, Z

def plotKde6d(df, params, mins, maxs, cutoffs):
    paramValues = []
    for p in params:
        tmp = df.loc[:, p]
        print(p)
        zip(paramValues, tmp)
        paramValues.append(tmp)
    positions, kernel, Z = calculateKde(paramValues, mins, maxs, cutoffs)

    xAxis = params[0]
    yAxis = params[1]
    xmin = mins[0]
    ymin = mins[1]
    xmax = maxs[0]
    ymax = maxs[1]
    # Plotting code below
    fig, ax = plt.subplots()
    plt.grid(True)
    plt.xlabel(xAxis)
    plt.ylabel(yAxis)
    plt.title(xAxis+"_v_"+yAxis)
    ax.use_sticky_edges = False
    q = ax.imshow(np.rot90(Z), cmap=plt.cm.gist_earth_r,
        extent=[xmin, xmax, ymin, ymax], aspect="auto")
    ax.set_xlim([xmin, xmax])
    ax.set_ylim([ymin, ymax])
    ax.set_xticks([6,7,8,9,10,11,12])
    axes = plt.gca()

    #save and show plot figure
    today = date.today()
    today = today.strftime("%Y_%m_%d")
    plt.colorbar(q)
    plt.savefig(today+"_"+xAxis+"_v_"+yAxis+".pdf", bbox_inches='tight')
    plt.show()

    sns.kdeplot(df[xAxis], df[yAxis], shade=False, cbar=True, cmap="inferno_r", levels = 10, shade_lowest=False)

    # Extract kde and write into output file
    Z = kernel(positions).T

    # Output in date_xAxis_v_yAxis format
    #TODO: add in a way to name all the columns from here
    file = open(outputDirectory+today+'_allGeometryKde.csv','w')
    for currentIndex,elem in enumerate(Z):
        s1 = '%f, %f, %f, %f, %f, %f, %f\n'%(positions[0][currentIndex], positions[1][currentIndex], positions[2][currentIndex], positions[3][currentIndex], positions[4][currentIndex], positions[5][currentIndex], Z[currentIndex]*10000000 )
        file.write(s1)
    file.close()
    return Z

#Main
#change this output to a more dynamic directory
outputDirectory = "C:\\Users\\gjowl\\Documents\\"
dfPath = "C:\\Users\\gjowl\\Downloads\\2020_09_23_kdeData.csv"
parameters = pd.read_csv(dfPath, nrows=0).columns.tolist()
df = pd.read_csv(dfPath)

dist = "Distance"
ang = "Angle"
rot1 = "Rot1"
rot2 = "Rot2"
z1 = "Z1"
z2 = "Z2"

mins = np.array([6, -100, 0, 0, 0, 0])
maxs = np.array([12, 100, 6, 6, 100, 100])
cutoffs = np.array([20j, 20j, 20j, 20j, 20j, 20j])

plotKde6d(df, parameters, mins, maxs, cutoffs)
