"""
Created on Mon Sep 13 18:37:30 2021

@author: gjowl
"""
"""
This file is used to adjust the kde plot of axialRotation and zShift so that it only accepts values within the symmetric region
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
        X, Y = np.mgrid[xmin:xmax:24j, ymin:ymax:40j]
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
    plt.grid(True)
    plt.xlabel(xAxis)
    plt.ylabel(yAxis)
    plt.title(xAxis+"_v_"+yAxis)
    ax.use_sticky_edges = False
    q = ax.imshow(np.rot90(Z), cmap=plt.cm.gist_earth_r,
        extent=[xmin, xmax, ymin, ymax], aspect="auto")
    x = df.loc[:, xAxis]
    y = df.loc[:, yAxis]
    #ax.plot(x, y, 'k.', markersize=2)
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
    plt.colorbar(q)
    plt.savefig(today+"_"+xAxis+"_v_"+yAxis+".pdf", bbox_inches='tight')
    plt.show()

    sns.kdeplot(df[xAxis], df[yAxis], shade=False, cbar=True, cmap="inferno_r", levels = 10, shade_lowest=False)

    # Extract kde and write into output file
    Z = kernel(positions).T

    # Output in date_xAxis_v_yAxis format

    #fid = open(today+"_"+xAxis+"_v_"+yAxis+"_adjustedKde.csv",'w')
    #for currentIndex,elem in enumerate(positions):
    for currentIndex,elem in enumerate(Z):
        s1 = '%f, %f, %f\n'%(positions[0][currentIndex], positions[1][currentIndex], Z[currentIndex] )
        #s1 = '%f, %f, %f, %f, %f, %f, %f\n'%(positions[0][currentIndex], positions[1][currentIndex], positions[2][currentIndex], positions[3][currentIndex], positions[4][currentIndex], positions[5][currentIndex], Z[currentIndex]*10000000 )
    #    fid.write(s1)
    #fid.close()
    return Z

def plotKdeOverlay(dfKde, xData, yData, xAxis, yAxis, type):
    #Variable set up depending on data that I'm running
    if xAxis == "Distance":
        xmin = 6
        xmax = 12
        ymin = -100
        ymax = 100
        X, Y = np.mgrid[xmin:xmax:24j, ymin:ymax:40j]
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
    x = dfKde.loc[:, xAxis]
    y = dfKde.loc[:, yAxis]

    if type == 1:
        name = "Negative"
    if type == 2:
        name = "PositiveVDW"
    if type == 3:
        name = "Clashing"
    if type == 4:
        name = "all"
    if type == 5:
        name = "DimerNoIMM1"
    #Kernel Density Estimate Calculation
    positions = np.vstack([X.ravel(), Y.ravel()])
    values = np.vstack([x, y])
    kernel = stats.gaussian_kde(values)
    kernel.set_bandwidth(bw_method='silverman')
    Z = np.reshape(kernel(positions).T, X.shape)

    # Plotting code below
    fig, ax = plt.subplots()
    plt.grid(True)
    plt.xlabel(xAxis)
    plt.ylabel(yAxis)
    plt.title(xAxis+"_v_"+yAxis+"_"+name)
    ax.use_sticky_edges = False
    q = ax.imshow(np.rot90(Z), cmap=plt.cm.gist_earth_r,
        extent=[xmin, xmax, ymin, ymax], aspect="auto")
    ax.plot(xData, yData, 'k.', markersize=3, color = "Red")
    x = dfKde.loc[:, xAxis]
    y = dfKde.loc[:, yAxis]
    #ax.plot(x, y, 'k.', markersize=2)
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
    plt.colorbar(q)
    plt.savefig(today+"_"+xAxis+"_v_"+yAxis+"_"+name+".png", bbox_inches='tight')
    plt.show()

    figSNS, axSNS = plt.subplots()
    plt.title(xAxis+"_v_"+yAxis+"_"+name)
    if xAxis == "Distance":
        sns.kdeplot(dfKde[xAxis], dfKde[yAxis], shade=False, cbar=True, cmap="inferno_r", levels = 5, shade_lowest=False, ax=axSNS)
    else:
        sns.kdeplot(dfKde[xAxis], dfKde[yAxis], shade=False, cbar=True, cmap="inferno_r", levels = 10, shade_lowest=False, ax=axSNS)
    axSNS.plot(xData, yData, 'k.', markersize=3, color = "Blue")
    plt.savefig(today+"_"+xAxis+"_v_"+yAxis+"_"+name+"_contour.png", bbox_inches='tight')

    # Extract kde and write into output file
    Z = kernel(positions).T

    # Output in date_xAxis_v_yAxis format

    fid = open(today+"_"+xAxis+"_v_"+yAxis+"_kde.csv",'w')
    #for currentIndex,elem in enumerate(positions):
    for currentIndex,elem in enumerate(Z):
        s1 = '%f, %f, %f\n'%(positions[0][currentIndex], positions[1][currentIndex], Z[currentIndex] )
        #s1 = '%f, %f, %f, %f, %f, %f, %f\n'%(positions[0][currentIndex], positions[1][currentIndex], positions[2][currentIndex], positions[3][currentIndex], positions[4][currentIndex], positions[5][currentIndex], Z[currentIndex]*10000000 )
        fid.write(s1)
    fid.close()
    return Z

##############################################
#               FILE INPUT
##############################################

#name = "C:\\Users\\gjowl\\Documents\\2021_09_25_Rot1_v_Rot2_kde.csv"
name = "C:\\Users\\gjowl\\Downloads\\2020_09_23_kdeData.csv"
#name = "C:\\Users\\gjowl\\Documents\\Senes Lab\\Design_data\\Design_files\\designsSoFar.csv"

# Gets the header line to be used for the analysis
header = pd.read_csv(name, index_col=0, nrows=0).columns.tolist()
df = pd.read_csv(name, sep=",")

##############################################
#           MAKE SHEETS FOR OUTPUT
##############################################
tmp = df[df["Rot1"] < df["Rot2"]+5]
tmp = tmp[tmp["Rot1"] > tmp["Rot2"]-5]

##############################################
#          PLOT KDE OVERLAYS
##############################################
dfPath = "C:\\Users\\gjowl\\Downloads\\2020_09_23_kdeData.csv"
dfKde = pd.read_csv(dfPath)

ax1  = tmp.loc[:, "Rot1"]
ax2  = tmp.loc[:, "Rot2"]

print(len(tmp))

#Plot
plotKde(tmp, "Rot1", "Rot2")
#plotKdeOverlay(dfKde, ax1, ax2, "Rot1", "Rot2", 1)

tmp = df[df["Z1"] < df["Z2"]+.5]
tmp = tmp[tmp["Z1"] > tmp["Z2"]-.5]

print(len(tmp))

z1  = df.loc[:, "Z1"]
z2  = df.loc[:, "Z2"]
plotKde(tmp, "Z1", "Z2")

##############################################
#               FILE OUTPUT
##############################################

#with pd.ExcelWriter('C:\\Users\\gjowl\\Documents\\Senes Lab\\Design_data\\Analysis files\\2021_10_07_dataAnalysis.xlsx',engine='xlsxwriter') as writer:
#    df.to_excel(writer,sheet_name='Total Energy < 0',startrow=0 , startcol=0)
