import matplotlib.pyplot as plt
import matplotlib.colors
import pandas as pd
import os
import sys
import numpy as np
from scipy import stats

"""
Run as:
    python3 plotGeometryKde.py [inputFile] [kdeFile]
"""
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

def plotKdeOverlay(kdeZScores, xAxis, yAxis, fluor, filename, outputDir):
    # Plotting code below
    fig, ax = plt.subplots()
    # plotting labels and variables 
    plt.grid(False)
    plt.xlabel("Distance (Å)")
    plt.ylabel("Angle (°)")
    plt.title(filename)
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
    
    # Plot datapoints onto the graph with fluorescence as size
    # get colormap shades of green
    cmap = plt.cm.Reds
    cmap = cmap.reversed()
    # get min and max of the data
    min_val = np.min(fluor)
    max_val = np.max(fluor)
    # flip the data so that the min is at the top of the colorbar
    #norm = matplotlib.colors.Normalize(vmin=40, vmax=100) # TODO: change this to the min and max of the data
    norm = matplotlib.colors.Normalize(vmin=-50, vmax=-5) # TODO: change this to the min and max of the data
    print(norm(fluor))
    ax.scatter(xAxis, yAxis, c=cmap(norm(fluor)), s=30, alpha=0.5)
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    # normalize the fluorescent data to the range of the colorbar
    sm.set_array([])  # only needed for matplotlib < 3.1
    fig.colorbar(sm)
    # add the number of datapoints to the plot
    plt.text(xmin-1, ymax+7, "# Sequences = " + str(len(xAxis)), fontsize=10)
    #ax.scatter(xAxis, yAxis, c='r', s=5, marker='o', alpha=0.5)
    # Plot data points onto the graph with fluorescence as color
    #ax.scatter(xAxis, yAxis, c=fluor, s=5, marker='o', alpha=0.5)
    # Plot the datapoints onto the graph
    #ax.scatter(xAxis, yAxis, c='r', s=5, marker='o', alpha=0.5)
    ax.set_xlim([xmin, xmax])
    ax.set_ylim([ymin, ymax])
    ax.set_xticks([6,7,8,9,10,11,12])
    axes = plt.gca()

    #plt.colorbar(q)
    plt.savefig(outputDir+filename+".png", bbox_inches='tight', dpi=150)
    plt.close()

# read in kde file from command line, or default to 2020_09_23_kdeData.csv
projectDir = os.getcwd()+'/'
kdeFile = projectDir + '2020_09_23_kdeData.csv'
inputFile = sys.argv[1]
# copy and paste some code for writing the kde data to a file
df_kde = pd.read_csv(kdeFile)
df_data = pd.read_csv(inputFile)
# set xAxis and yAxis variables
xAxis = 'xShift'
yAxis = 'crossingAngle'
data = 'EnergyScore'

df_data = df_data[df_data['StartSequence'] == df_data['Sequence']]
#df_data = df_data[df_data['MaltosePercentDiff'] > -100]
#df_data = df_data[df_data['PercentGpa'] > 60]
# get the x and y axes data to be plotted from the dataframe
x = df_data.loc[:, xAxis]
y = df_data.loc[:, yAxis]
fluor = df_data[data].values
# get the kde plot for the geometry data
kdeZScores = getKdePlotZScoresplotKdeOverlayForDfList(df_kde, 'Distance', 'Angle')
# TODO: run on just design sequences
# plot the kde plot with an overlay of the input dataset   
plotKdeOverlay(kdeZScores, x, y, fluor, "GxxxG_-40to-5_"+data, projectDir)
# TODO: figure out what might be a good point to drop monomers from data