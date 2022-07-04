# -*- coding: utf-8 -*-
"""
Created on Fri Mar  5 15:44:57 2021

@author: gjowl
"""
from datetime import date
from scipy import stats
from matplotlib import gridspec
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
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
    ax.plot(x, y, 'k.', markersize=2)
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

    fid = open(today+"_"+xAxis+"_v_"+yAxis+"_kde.csv",'w')
    #for currentIndex,elem in enumerate(positions):
    for currentIndex,elem in enumerate(Z):
        s1 = '%f, %f, %f\n'%(positions[0][currentIndex], positions[1][currentIndex], Z[currentIndex] )
        #s1 = '%f, %f, %f, %f, %f, %f, %f\n'%(positions[0][currentIndex], positions[1][currentIndex], positions[2][currentIndex], positions[3][currentIndex], positions[4][currentIndex], positions[5][currentIndex], Z[currentIndex]*10000000 )
        fid.write(s1)
    fid.close()
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


##############################################
#            PLOT KERNEL DENSITY
##############################################
#fig, ax = plt.subplots(1, 1, figsize=(1,800))
plotKde(df, dist, ang)
plotKde(df, rot1, rot2)
plotKde(df, z1, z2)

#kde = stats.gaussian_kde(values)
#density = kde(values)

#fig, ax = plt.subplots(subplot_kw=dict(projection='3d'))
#x, y = values
#ax.scatter(x, y, c=density)
#plt.show()

#x=np.array([1, 2, 3, 4, 5])

# making subplots
#fig, ax = plt.subplots(2, 2)

# set data with subplots and plot
#ax[0, 0].plot(x, x)
#ax[0, 1].plot(x, x*2)
#ax[1, 0].plot(x, x*x)
#ax[1, 1].plot(x, x*x*x)

# set the spacing between subplots
#plt.show()

#Contour plot (imshow causes it to squeeze the image)
#fig = plt.figure()
#ax = fig.gca()
#ax.set_xlim(xmin, xmax)
#ax.set_ylim(ymin, ymax)
# Contourf plot
#cfset = ax.contourf(X, Y, Z, cmap='Blues')
## Or kernel density estimate plot instead of the contourf plot
#ax.imshow(np.rot90(Z), cmap='Blues', extent=[xmin, xmax, ymin, ymax])
# Contour plot
#cset = ax.contour(X, Y, Z, colors='k')
# Label plot
#ax.clabel(cset, inline=1, fontsize=10)
#ax.set_xlabel('Distance')
#ax.set_ylabel('Angle')
