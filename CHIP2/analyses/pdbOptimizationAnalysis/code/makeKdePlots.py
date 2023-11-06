import os, sys, pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

def plotGeomKde(df_kde, df_data, dataColumn, outputDir, xAxis, yAxis, roundToNearest=5, minY=-100000, maxY=-100000, reverseColormap=False):
    # get the x and y axes data to be plotted from the dataframe
    x = df_data.loc[:, xAxis]
    y = df_data.loc[:, yAxis]
    energies = df_data[dataColumn].values
    # get the kde plot for the geometry data
    kdeZScores = getKdePlotZScoresplotKdeOverlayForDfList(df_kde, 'Distance', 'Angle')
    # plot the kde plot with an overlay of the input dataset   
    plotKdeOverlay(kdeZScores, x, y, energies, dataColumn, outputDir, roundToNearest, minY, maxY, reverseColormap)

def plotKdeOverlay(kdeZScores, xAxis, yAxis, data, dataColumn, outputDir, roundToNearest, minY, maxY, reverseColormap):
    # Plotting code below
    fig, ax = plt.subplots()
    # plotting labels and variables 
    plt.grid(False)
    plt.xlabel("Distance (Å)")
    plt.ylabel("Angle (°)")
    plt.title("")
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
    if reverseColormap:
        cmap = cmap.reversed()
    # get min and max of the data rounded to the nearest 5
    if minY == -100000:
        minY = int(np.floor(np.min(data)/5)*roundToNearest)
        maxY = int(np.ceil(np.max(data)/5)*roundToNearest)
    # flip the data so that the min is at the top of the colorbar
    norm = matplotlib.colors.Normalize(vmin=minY, vmax=maxY) 
    ax.scatter(xAxis, yAxis, c=cmap(norm(data)), s=10, alpha=0.5)
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    # normalize the fluorescent data to the range of the colorbar
    sm.set_array([])  # only needed for matplotlib < 3.1
    fig.colorbar(sm)
    # add the number of datapoints to the plot
    plt.text(xmin-1, ymax+12, "# Sequences = " + str(len(xAxis)), fontsize=10)
    ax.set_xlim([xmin, xmax])
    ax.set_ylim([ymin, ymax])
    ax.set_xticks([6,7,8,9,10,11,12])
    axes = plt.gca()

    # output the number of sequences in the dataset onto plot
    plt.tight_layout()
    plt.savefig(f'{outputDir}/kdeOverlay_{dataColumn}.png', bbox_inches='tight', dpi=150)
    plt.close()

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

# read in the command line arguments
kdeFile = sys.argv[1]
dataFile = sys.argv[2]
outputDir = sys.argv[3]

# read the files in as dataframes
kdeDf = pd.read_csv(kdeFile)
dataDf = pd.read_csv(dataFile)

# get the current working directory
cwd = os.getcwd()

# only keep the unique sequence with best total energy
df = dataDf.sort_values(by=['Total'], ascending=True)
# keep only unique sequences, and the unique sequence with the lowest total energy
df = df.drop_duplicates(subset=['Sequence'], keep='first')
df = df[df['Total'] < 0]
#df = df[df['PercentStd'] < 15]

# plot the kde data
plotGeomKde(kdeDf, df, 'Total', outputDir, 'preOptimizeXShift', 'preOptimizeCrossingAngle', reverseColormap=True)
minY, maxY = 0, 1
plotGeomKde(kdeDf, df, 'PercentGpA', outputDir, 'preOptimizeXShift', 'preOptimizeCrossingAngle', 1, minY, maxY)