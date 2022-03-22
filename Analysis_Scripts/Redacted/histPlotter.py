# @Author: Gilbert Loiseau
# @Date:   2021-10-22
# @Filename: histPlotter.py
# @Last modified by:   Gilbert Loiseau
# @Last modified time: 2021-11-28



from datetime import date
from scipy import stats
from matplotlib import gridspec
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns

##############################################
#                 FUNCTIONS
##############################################
def plotKde(df, xAxis, yAxis):
    #Variable set up depending on data that I'm running
    if xAxis == "xShift":
        xmin = 6
        xmax = 12
        ymin = -100
        ymax = 100
        X, Y = np.mgrid[xmin:xmax:24j, ymin:ymax:40j]
    elif xAxis == "zShift":
        xmin = 0
        xmax = 6
        ymin = 0
        ymax = 6
        X, Y = np.mgrid[xmin:xmax:24j, ymin:ymax:24j]
    elif xAxis == "axialRotation":
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
    if xAxis == "xShift":
           ax.set_xticks([6,7,8,9,10,11,12])
    elif xAxis == "axialRotation":
           ax.set_xticks([0,20,40,60,80,100])
    elif xAxis == "zShift":
           ax.set_xticks([0,1,2,3,4,5,6])
    axes = plt.gca()

    #save and show plot figure
    today = date.today()
    today = today.strftime("%Y_%m_%d")
    plt.colorbar(q)
    #plt.savefig(today+"_"+xAxis+"_v_"+yAxis+".pdf", bbox_inches='tight')
    plt.show()

    #sns.kdeplot(df[xAxis], df[yAxis], shade=False, cbar=True, cmap="inferno_r", levels = 10, shade_lowest=False)

    # Extract kde and write into output file
    Z = kernel(positions).T

    # Output in date_xAxis_v_yAxis format

    #fid = open(today+"_"+xAxis+"_v_"+yAxis+"_kde_1.csv",'w')
    #for currentIndex,elem in enumerate(positions):
    #for currentIndex,elem in enumerate(Z):
        #s1 = '%f, %f, %f\n'%(positions[0][currentIndex], positions[1][currentIndex], Z[currentIndex] )
        #s1 = '%f, %f, %f, %f, %f, %f, %f\n'%(positions[0][currentIndex], positions[1][currentIndex], positions[2][currentIndex], positions[3][currentIndex], positions[4][currentIndex], positions[5][currentIndex], Z[currentIndex]*10000000 )
        #fid.write(s1)
    #fid.close()
    #return Z

def getCountsPerDensityArrays(df1, df2, numberBins, binSize):
    bins = np.array([])
    density = np.array([])
    binCount1 = np.array([])
    binCount2 = np.array([])

    i=1
    while i<numberBins:
        currDensity = i*binSize
        tmpdf1 = df1[df1["angleDistDensity"] < currDensity]
        tmpdf2 = df2[df2["angleDistDensity"] < currDensity]
        bins = np.append(bins, currDensity-binSize)
        density = np.append(density, currDensity)
        binCount1 = np.append(binCount1, len(tmpdf1))
        binCount2 = np.append(binCount2, len(tmpdf2))
        #print(tmpdf1)
        i+=1
    return bins, density, binCount1, binCount2

def addArraysToDataframe(bins, density, binCount1, binCount2):
    df = pd.DataFrame()
    df["Bins"] = bins
    df["Density"] = density
    df["Count1"] = binCount1
    df["Count2"] = binCount2
    return df

def plotHistograms(df):
    # Plotting code below
    fig, ax = plt.subplots()
    plt.xlabel('Density')
    plt.ylabel('Count')
    plt.title('Count by density')
    #ax.set_xlim([0, 1])
    densityArray = df['Count1'].to_numpy()
    ax.set_xticks([0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1])
    #ax.set_ylim([ymin, ymax])
    print(df['Count1'])
    print(densityArray)

    plt.show()
    plt.bar(df['Bins'], df['Count1'])
    plt.show()
    plt.bar(df['Density'], df['Count2'])
    plt.show()

def plotHistogram(df):
    fig, ax = plt.subplots()
    plt.xlabel('Density')
    plt.ylabel('Count')
    plt.title('Count by density')
    print(ax.hist(df["angleDistDensity"], bins=10))
    plt.show()

#Main code
newGeometries = "C:\\Users\\gjowl\\Downloads\\2021_10_22_geometryDensityFile(2).csv"
oldGeometries = "C:\\Users\\gjowl\\Downloads\\2021_10_11_geometryDensityFile.csv"

# Gets the header line to be used for the analysis
parameters = pd.read_csv(oldGeometries, nrows=0).columns.tolist()
dfOld = pd.read_csv(oldGeometries, sep=",")
dfNew = pd.read_csv(newGeometries, sep=",")

plotHistogram(dfOld)
plotHistogram(dfNew)
print(dfNew)

plotKde(dfOld, parameters[0], parameters[1])
plotKde(dfNew, parameters[0], parameters[1])
plotKde(dfOld, parameters[2], parameters[2])
plotKde(dfOld, parameters[3], parameters[3])
