import matplotlib.pyplot as plt
import matplotlib.colors
import pandas as pd
import os
import sys
import numpy as np
from scipy import stats

"""
edited version of plotGeomKde.py to plot the kde for the 2020_09_23_kdeData.csv file with 
an overlay of an input dataframe. The plotGeomKde function is the driver function and the others are helper functions

"""
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
def plotGeomKde(df_kde, df_data, dataColumn):
    # read in kde file from command line, or default to 2020_09_23_kdeData.csv
    projectDir = os.getcwd()+'/'
=======
def plotGeomKde(df_kde, df_data, dataColumn, outputDir):
    # read in kde file from command line, or default to 2020_09_23_kdeData.csv
>>>>>>> ad76af7087793a7c3c58fcc8c653ea5605f2b2ff
=======
def plotGeomKde(df_kde, df_data, dataColumn, outputDir):
    # read in kde file from command line, or default to 2020_09_23_kdeData.csv
>>>>>>> ad76af7087793a7c3c58fcc8c653ea5605f2b2ff
=======
def plotGeomKde(df_kde, df_data, dataColumn, outputDir):
    # read in kde file from command line, or default to 2020_09_23_kdeData.csv
>>>>>>> ad76af7087793a7c3c58fcc8c653ea5605f2b2ff
=======
def plotGeomKde(df_kde, df_data, dataColumn, outputDir):
    # read in kde file from command line, or default to 2020_09_23_kdeData.csv
>>>>>>> 526550a3041fc0669e9d118b0c727dbcc999064b
=======
def plotGeomKde(df_kde, df_data, dataColumn, outputDir):
    # read in kde file from command line, or default to 2020_09_23_kdeData.csv
>>>>>>> aff5e515ed04cfd4d742cd0dd2b778f297359cb8
    df_data = df_data.drop_duplicates('crossingAngle',keep='first')

    # set xAxis and yAxis variables
    xAxis = 'xShift'
    yAxis = 'crossingAngle'

    # get the x and y axes data to be plotted from the dataframe
    x = df_data.loc[:, xAxis]
    y = df_data.loc[:, yAxis]
    energies = df_data[dataColumn].values

    # get the kde plot for the geometry data
    kdeZScores = getKdePlotZScoresplotKdeOverlayForDfList(df_kde, 'Distance', 'Angle')

    # plot the kde plot with an overlay of the input dataset   
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
    plotKdeOverlay(kdeZScores, x, y, energies, dataColumn, projectDir)
=======
    plotKdeOverlay(kdeZScores, x, y, energies, dataColumn, outputDir)
>>>>>>> ad76af7087793a7c3c58fcc8c653ea5605f2b2ff
=======
    plotKdeOverlay(kdeZScores, x, y, energies, dataColumn, outputDir)
>>>>>>> ad76af7087793a7c3c58fcc8c653ea5605f2b2ff
=======
    plotKdeOverlay(kdeZScores, x, y, energies, dataColumn, outputDir)
>>>>>>> ad76af7087793a7c3c58fcc8c653ea5605f2b2ff
=======
    plotKdeOverlay(kdeZScores, x, y, energies, dataColumn, outputDir)
>>>>>>> 526550a3041fc0669e9d118b0c727dbcc999064b
=======
    plotKdeOverlay(kdeZScores, x, y, energies, dataColumn, outputDir)
>>>>>>> aff5e515ed04cfd4d742cd0dd2b778f297359cb8

def getKdePlotZScoresplotKdeOverlayForDfList(df_kde, xAxis, yAxis):
    # hardcoded variable set up for plot limits
    xmin, xmax, ymin, ymax = 6, 12, -100, 100
    # create the kde grid (hardcoded 24 by 40)
    X, Y = np.mgrid[xmin:xmax:24j, ymin:ymax:40j]

    # get the x and y axes data to be plotted from the dataframe
    x = df_kde.loc[:, xAxis]
    y = df_kde.loc[:, yAxis]

    #Kernel Density Estimate Calculation
    positions = np.vstack([X.ravel(), Y.ravel()])
    values = np.vstack([x, y])
    kernel = stats.gaussian_kde(values)
    kernel.set_bandwidth(bw_method='silverman')
    # Z-scores: the part that actually plots the kde
    Z = np.reshape(kernel(positions).T, X.shape)
    return Z

<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
def plotKdeOverlay(kdeZScores, xAxis, yAxis, data, filename, outputDir):
=======
def plotKdeOverlay(kdeZScores, xAxis, yAxis, data, dataColumn, outputDir):
>>>>>>> ad76af7087793a7c3c58fcc8c653ea5605f2b2ff
=======
def plotKdeOverlay(kdeZScores, xAxis, yAxis, data, dataColumn, outputDir):
>>>>>>> ad76af7087793a7c3c58fcc8c653ea5605f2b2ff
=======
def plotKdeOverlay(kdeZScores, xAxis, yAxis, data, dataColumn, outputDir):
>>>>>>> ad76af7087793a7c3c58fcc8c653ea5605f2b2ff
=======
def plotKdeOverlay(kdeZScores, xAxis, yAxis, data, dataColumn, outputDir):
>>>>>>> 526550a3041fc0669e9d118b0c727dbcc999064b
=======
def plotKdeOverlay(kdeZScores, xAxis, yAxis, data, dataColumn, outputDir):
>>>>>>> aff5e515ed04cfd4d742cd0dd2b778f297359cb8
    # Plotting code below
    fig, ax = plt.subplots()
    # plotting labels and variables 
    plt.grid(False)
    plt.xlabel("Distance (Å)")
    plt.ylabel("Angle (°)")
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
    plt.title(filename)
=======
    plt.title(dataColumn)
>>>>>>> ad76af7087793a7c3c58fcc8c653ea5605f2b2ff
=======
    plt.title(dataColumn)
>>>>>>> ad76af7087793a7c3c58fcc8c653ea5605f2b2ff
=======
    plt.title(dataColumn)
>>>>>>> ad76af7087793a7c3c58fcc8c653ea5605f2b2ff
=======
    plt.title(dataColumn)
>>>>>>> 526550a3041fc0669e9d118b0c727dbcc999064b
=======
    plt.title(dataColumn)
>>>>>>> aff5e515ed04cfd4d742cd0dd2b778f297359cb8
    # Setup for plotting output
    plt.rc('font', size=10)
    plt.rc('xtick', labelsize=10)
    plt.rc('ytick', labelsize=10)
    # hardcoded variable set up for plot limits
    xmin, xmax, ymin, ymax = 6, 12, -100, 100
    # setup kde plot for original geometry dataset
    ax.use_sticky_edges = False
    q = ax.imshow(np.rot90(kdeZScores), cmap=plt.cm.Blues,
        extent=[xmin, xmax, ymin, ymax], aspect="auto")
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
    
    # Plot datapoints onto the graph with fluorescence as size
    # get colormap shades of green
    cmap = plt.cm.Reds
    #cmap = cmap.reversed()
=======
=======
>>>>>>> ad76af7087793a7c3c58fcc8c653ea5605f2b2ff
=======
>>>>>>> ad76af7087793a7c3c58fcc8c653ea5605f2b2ff
=======
>>>>>>> 526550a3041fc0669e9d118b0c727dbcc999064b
=======
>>>>>>> aff5e515ed04cfd4d742cd0dd2b778f297359cb8
    # Plot datapoints onto the graph with fluorescence as size
    # get colormap shades of green
    cmap = plt.cm.Reds
    cmap = cmap.reversed()
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
>>>>>>> ad76af7087793a7c3c58fcc8c653ea5605f2b2ff
=======
>>>>>>> ad76af7087793a7c3c58fcc8c653ea5605f2b2ff
=======
>>>>>>> ad76af7087793a7c3c58fcc8c653ea5605f2b2ff
=======
>>>>>>> 526550a3041fc0669e9d118b0c727dbcc999064b
=======
>>>>>>> aff5e515ed04cfd4d742cd0dd2b778f297359cb8
    # get min and max of the data
    min_val = np.min(data)
    max_val = np.max(data)
    # flip the data so that the min is at the top of the colorbar
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
    norm = matplotlib.colors.Normalize(vmin=50, vmax=100) # TODO: change this to the min and max of the data
    #norm = matplotlib.colors.Normalize(vmin=-50, vmax=-5) # TODO: change this to the min and max of the data
=======
    norm = matplotlib.colors.Normalize(vmin=-55, vmax=-5) # TODO: change this to the min and max of the data
>>>>>>> ad76af7087793a7c3c58fcc8c653ea5605f2b2ff
=======
    norm = matplotlib.colors.Normalize(vmin=-55, vmax=-5) # TODO: change this to the min and max of the data
>>>>>>> ad76af7087793a7c3c58fcc8c653ea5605f2b2ff
=======
    norm = matplotlib.colors.Normalize(vmin=-55, vmax=-5) # TODO: change this to the min and max of the data
>>>>>>> ad76af7087793a7c3c58fcc8c653ea5605f2b2ff
=======
    norm = matplotlib.colors.Normalize(vmin=-55, vmax=-5) # TODO: change this to the min and max of the data
>>>>>>> 526550a3041fc0669e9d118b0c727dbcc999064b
=======
    norm = matplotlib.colors.Normalize(vmin=-55, vmax=-5) # TODO: change this to the min and max of the data
>>>>>>> aff5e515ed04cfd4d742cd0dd2b778f297359cb8
    ax.scatter(xAxis, yAxis, c=cmap(norm(data)), s=30, alpha=0.5)
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    # normalize the fluorescent data to the range of the colorbar
    sm.set_array([])  # only needed for matplotlib < 3.1
    fig.colorbar(sm)
    # add the number of datapoints to the plot
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
    plt.text(xmin-1, ymax+7, "# Sequences = " + str(len(xAxis)), fontsize=10)
    #ax.scatter(xAxis, yAxis, c='r', s=5, marker='o', alpha=0.5)
    # Plot data points onto the graph with fluorescence as color
    #ax.scatter(xAxis, yAxis, c=fluor, s=5, marker='o', alpha=0.5)
    # Plot the datapoints onto the graph
    #ax.scatter(xAxis, yAxis, c='r', s=5, marker='o', alpha=0.5)
=======
    plt.text(xmin-1, ymax+7, "# Geometries = " + str(len(xAxis)), fontsize=10)
>>>>>>> ad76af7087793a7c3c58fcc8c653ea5605f2b2ff
=======
    plt.text(xmin-1, ymax+7, "# Geometries = " + str(len(xAxis)), fontsize=10)
>>>>>>> ad76af7087793a7c3c58fcc8c653ea5605f2b2ff
=======
    plt.text(xmin-1, ymax+7, "# Geometries = " + str(len(xAxis)), fontsize=10)
>>>>>>> ad76af7087793a7c3c58fcc8c653ea5605f2b2ff
=======
    plt.text(xmin-1, ymax+7, "# Geometries = " + str(len(xAxis)), fontsize=10)
>>>>>>> 526550a3041fc0669e9d118b0c727dbcc999064b
=======
    plt.text(xmin-1, ymax+7, "# Geometries = " + str(len(xAxis)), fontsize=10)
>>>>>>> aff5e515ed04cfd4d742cd0dd2b778f297359cb8
    ax.set_xlim([xmin, xmax])
    ax.set_ylim([ymin, ymax])
    ax.set_xticks([6,7,8,9,10,11,12])
    axes = plt.gca()
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD

    #plt.colorbar(q)
    plt.savefig(outputDir+filename+".png", bbox_inches='tight', dpi=150)
=======
    plt.savefig(outputDir+"/kdeOverlay.png", bbox_inches='tight', dpi=150)
>>>>>>> ad76af7087793a7c3c58fcc8c653ea5605f2b2ff
=======
    plt.savefig(outputDir+"/kdeOverlay.png", bbox_inches='tight', dpi=150)
>>>>>>> ad76af7087793a7c3c58fcc8c653ea5605f2b2ff
=======
    plt.savefig(outputDir+"/kdeOverlay.png", bbox_inches='tight', dpi=150)
>>>>>>> ad76af7087793a7c3c58fcc8c653ea5605f2b2ff
=======
    plt.savefig(outputDir+"/kdeOverlay.png", bbox_inches='tight', dpi=150)
>>>>>>> 526550a3041fc0669e9d118b0c727dbcc999064b
=======
    # output the number of sequences in the dataset onto plot
    #plt.text(xmin-1, ymax+10, "# N = " + str(len(xAxis)), fontsize=10)
    plt.savefig(outputDir+"/kdeOverlay.png", bbox_inches='tight', dpi=150)
>>>>>>> aff5e515ed04cfd4d742cd0dd2b778f297359cb8
    plt.close()

#TODO:
# is it possible to get the kde density for a single point?
# if so, do that for each geometric parameter
