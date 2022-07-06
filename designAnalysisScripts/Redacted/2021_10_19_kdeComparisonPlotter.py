"""
Created on Mon Sep 13 18:37:30 2021

@author: gjowl
"""
"""
This file is used to analyze the data from my sequence designs in an automated
way so that I don't have to manually do it every single time after the designs
are finished. It should take and read a file and set up all of the analysis for me.
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
def plotKde(df, xAxis, yAxis):
    #Variable set up depending on data that I'm running
    if xAxis == "Distance":
        xmin = 6
        xmax = 12
        ymin = -100
        ymax = 100
        X, Y = np.mgrid[xmin:xmax:24j, ymin:ymax:20j]
    elif xAxis == "Z1":
        xmin = 0
        xmax = 6
        ymin = 0
        ymax = 6
        X, Y = np.mgrid[xmin:xmax:24j, ymin:ymax:24j]
    elif xAxis == "Rot1":
        xmin = 0
        xmax = 100
        ymin = 0
        ymax = 100
        X, Y = np.mgrid[xmin:xmax:40j, ymin:ymax:40j]
    x = df.loc[:, xAxis]
    y = df.loc[:, yAxis]
    #TODO: add in a way to plot another version of this data with percentiles
    #Kernel Density Estimate Calculation
    positions = np.vstack([X.ravel(), Y.ravel()])
    values = np.vstack([x, y])
    kernel = stats.gaussian_kde(values)
    kernel.set_bandwidth(bw_method='silverman')
    Z = np.reshape(kernel(positions).T, X.shape)

    # Plotting code below
    fig, ax = plt.subplots()
    plt.grid(False)
    plt.xlabel(xAxis + " (Å)")
    plt.ylabel(yAxis + " (°)")
    plt.title("Geometries From PDB Search")
    ax.use_sticky_edges = False
    q = ax.imshow(np.rot90(Z), cmap=plt.cm.Blues,
        extent=[xmin, xmax, ymin, ymax], aspect="auto")
    x = df.loc[:, xAxis]
    y = df.loc[:, yAxis]
    ax.plot(x, y, 'k.', markersize=1.33)
    #ax.margins(x=2, y=2)
    ax.set_xlim([xmin, xmax])
    ax.set_ylim([ymin, ymax])
    #ax.set_aspect(0.5)
    if xAxis == "Distance":
           ax.set_xticks([6,7,8,9,10,11,12])
    elif xAxis == "Rot1":
           ax.set_xticks([0,20,40,60,80,100])
    elif xAxis == "Z1":
           ax.set_xticks([0,1,2,3,4,5,6])
    axes = plt.gca()

    #save and show plot figure
    today = date.today()
    today = today.strftime("%Y_%m_%d")
    #plt.colorbar(q)
    plt.savefig("C:\\Users\\gjowl\\Documents\\test_plot.png", bbox_inches='tight', dpi=150)
    plt.show()
    plt.close()


    sns.kdeplot(df[xAxis], df[yAxis], shade=False, cbar=True, cmap="inferno_r", levels = 10, shade_lowest=False)

    # Extract kde and write into output file
    Z = kernel(positions).T

    # Output in date_xAxis_v_yAxis format

    #fid = open(today+"_"+xAxis+"_v_"+yAxis+"_kde_1.csv",'w')
    #for currentIndex,elem in enumerate(positions):
    for currentIndex,elem in enumerate(Z):
        s1 = '%f, %f, %f\n'%(positions[0][currentIndex], positions[1][currentIndex], Z[currentIndex] )
        #s1 = '%f, %f, %f, %f, %f, %f, %f\n'%(positions[0][currentIndex], positions[1][currentIndex], positions[2][currentIndex], positions[3][currentIndex], positions[4][currentIndex], positions[5][currentIndex], Z[currentIndex]*10000000 )
        #fid.write(s1)
    #fid.close()
    return Z

##############################################
#          Main Code
##############################################

dfPath = "C:\\Users\\gjowl\\Downloads\\2020_09_23_kdeData.csv"
df = pd.read_csv(dfPath)

dist = "Distance"
ang = "Angle"
rot1 = "Rot1"
rot2 = "Rot2"
z1 = "Z1"
z2 = "Z2"

dfPath = "C:\\Users\\gjowl\\Downloads\\2021_10_19_geometryDensityFile.csv"
df1 = pd.read_csv(dfPath)

##############################################
#            PLOT KERNEL DENSITY
##############################################
#fig, ax = plt.subplots(1, 1, figsize=(1,800))
#plotKde(df, dist, ang)
plotKde(df, dist, ang)

from sklearn.manifold import TSNE

RS=123
#tsne = TSNE(random_state=RS).fit_transform()
