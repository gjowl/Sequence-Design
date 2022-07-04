import matplotlib.pyplot as plt
import gc
import seaborn as sns
import numpy as np
import random
from datetime import date
from scipy import stats

"""
This file contains a list of plotting functions that are used in the following programs:
"""
# Plot histogram for dataframe and a given list of bins
def plotHistogramForDataframe(df, colName, binList, filename, outputDir):
    fig, ax = plt.subplots()
    df.hist(column=colName, bins=binList, figsize=(25,25), color='purple')
    title = filename
    plt.title(title)
    plt.savefig(outputDir+"_"+filename+"_"+colName+".png", bbox_inches='tight', dpi=150)
    plt.clf()
    plt.cla()
    plt.close('all')
    gc.collect()

# plot 2d scatterplot for a given dataframe and two columns
def plotScatterplotForDataframe(df, xColumnName, yColumnName, title, filename, outputDir):
    fig, ax = plt.subplots()
    plt.xticks(ticks=df[xColumnName].unique())
    plt.scatter(x=df[xColumnName], y=df[yColumnName], s=0.3)
    plt.title(title)
    plt.savefig(outputDir+filename+".png", bbox_inches='tight', dpi=150)
    plt.clf()

#SINGLE COLOR PLOTTING
# Plots the original kde density with the new points from given data
def plotOverlay(Z, df, title, xAxis, yAxis, xMax, xMin, yMax, yMin, filename, outputDir):
    # Plotting code below
    fig, ax = plt.subplots()
    plt.grid(False)
    plt.xlabel(xAxis + " (Å)")
    plt.ylabel(yAxis + " (°)")
    plt.title(title)
    ax.use_sticky_edges = False
    q = ax.imshow(np.rot90(Z), cmap=plt.cm.Blues,
        extent=[xMin, xMax, yMin, yMax], aspect="auto")

    xData = df['xShift']
    yData = df['crossingAngle']
    # Plots the datapoints onto the graph
    ax.plot(xData, yData, markersize=1.33, color = "Red")
    ax.set_xlim([xMin, xMax])
    ax.set_ylim([yMin, yMax])
    ax.set_xticks([6,7,8,9,10,11,12])
    axes = plt.gca()

    #save and show plot figure
    today = date.today()
    today = today.strftime("%Y_%m_%d")
    #plt.colorbar(q)
    plt.savefig(outputDir+filename+".png", bbox_inches='tight', dpi=150)
    plt.close()

def plotContour(dfKde, df, title, xAxis, yAxis, xMax, xMin, yMax, yMin, filename, outputDir):
    figSNS, axSNS = plt.subplots()
    sns.kdeplot(x=dfKde[xAxis], y=dfKde[yAxis], shade=False, cbar=True, cmap="inferno_r", levels = 10, thresh=False, ax=axSNS)
    # Plots the datapoints onto the graph
    axSNS.set_xlim([xMin, xMax])
    axSNS.set_ylim([yMin, yMax])
    plt.xlabel(xAxis + " (Å)")
    plt.ylabel(yAxis + " (°)")
    plt.title(title)
    xData = df['xShift']
    yData = df['crossingAngle']
    axSNS.plot(xData, yData, markersize=1.33, color = "Red")
    #plt.savefig(outputDir+xAxis+"_v_"+yAxis+"_contour.png", bbox_inches='tight', dpi=150)
    plt.savefig(outputDir+filename+"_contour.png", bbox_inches='tight', dpi=150)
    plt.close()

# Plot angle vs distance density plot for dataframe values
def plotKdeOverlay(dfKde, df, xAxis, yAxis, outputDir, num):
    #Variable set up depending on data that I'm running
    xMin = 6
    xMax = 12
    yMin = -100
    yMax = 100
    X, Y = np.mgrid[xMin:xMax:24j, yMin:yMax:40j]
    x = dfKde.loc[:, xAxis]
    y = dfKde.loc[:, yAxis]

    #Kernel Density Estimate Calculation
    positions = np.vstack([X.ravel(), Y.ravel()])
    values = np.vstack([x, y])
    kernel = stats.gaussian_kde(values)
    kernel.set_bandwidth(bw_method='silverman')
    Z = np.reshape(kernel(positions).T, X.shape)

    # Setup for plotting code
    fig, ax = plt.subplots()
    plt.rc('font', size=10)
    plt.rc('xtick', labelsize=10)
    plt.rc('ytick', labelsize=10)

    title = "Segment #"+str(num)
    filename = str(num)+"_Segment"

    plotOverlay(Z, df, title, xAxis, yAxis, xMax, xMin, yMax, yMin, filename, outputDir)
    plotContour(dfKde, df, title, xAxis, yAxis, xMax, xMin, yMax, yMin, filename, outputDir)
    plt.close()

# MULTICOLOR PLOTTING
# Plots the original kde density with the new points from multiple dataframes
def plotMultiColorOverlay(Z, title, xAxis, yAxis, xMax, xMin, yMax, yMin, dfList, filename, outputDir, seed):
    # Plotting code below
    fig, ax = plt.subplots()
    plt.grid(False)
    plt.xlabel(xAxis + " (Å)")
    plt.ylabel(yAxis + " (°)")
    plt.title(title)
    ax.use_sticky_edges = False
    q = ax.imshow(np.rot90(Z), cmap=plt.cm.Blues,
        extent=[xMin, xMax, yMin, yMax], aspect="auto")

    # get a list of random colors  
    number_of_colors = len(dfList)  
    random.seed(seed)
    colors = ["#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])
             for i in range(number_of_colors)]
    # loop through the dfs and plot them in different colors
    for df, randColor in zip(dfList, colors):
        plt.plot(df['xShift'], df['crossingAngle'], '.', color=randColor)
    
    # set the x and y lengths of the plot and xtick names
    ax.set_xlim([xMin, xMax])
    ax.set_ylim([yMin, yMax])
    ax.set_xticks([6,7,8,9,10,11,12])
    axes = plt.gca()

    #save and show plot figure
    today = date.today()
    today = today.strftime("%Y_%m_%d")
    plt.savefig(outputDir+filename+".png", bbox_inches='tight', dpi=150)
    plt.close()

def plotMultiColorContour(dfKde, title, xAxis, yAxis, xMax, xMin, yMax, yMin, dfList, filename, outputDir, seed):
    figSNS, axSNS = plt.subplots()
    sns.kdeplot(x=dfKde[xAxis], y=dfKde[yAxis], shade=False, cbar=True, cmap="inferno_r", levels = 10, thresh=False, ax=axSNS)

    # Setup for the plot
    axSNS.set_xlim([xMin, xMax])
    axSNS.set_ylim([yMin, yMax])
    plt.xlabel(xAxis + " (Å)")
    plt.ylabel(yAxis + " (°)")
    plt.title(title)

    # get a list of random colors
    number_of_colors = len(dfList)  
    random.seed(seed)
    colors = ["#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])
             for i in range(number_of_colors)]

    # loop through the dfs and plot them in different colors
    for df, randColor in zip(dfList, colors):
        plt.plot(df['xShift'], df['crossingAngle'], '.', color=randColor)
    # loop through the dfs and plot them in different colors
    plt.savefig(outputDir+filename+"_contour.png", bbox_inches='tight', dpi=150)
    plt.close()

# Plot angle vs distance density plot for dataframe values
def plotMultiColorKdeOverlay(dfKde, dfList, xAxis, yAxis, outputDir, seed):
    #Variable set up depending on data that I'm running
    #TODO: make these variables in config
    xMin = 6
    xMax = 12
    yMin = -100
    yMax = 100
    X, Y = np.mgrid[xMin:xMax:24j, yMin:yMax:40j]
    x = dfKde.loc[:, xAxis]
    y = dfKde.loc[:, yAxis]

    #Kernel Density Estimate Calculation
    positions = np.vstack([X.ravel(), Y.ravel()])
    values = np.vstack([x, y])
    kernel = stats.gaussian_kde(values)
    kernel.set_bandwidth(bw_method='silverman')
    Z = np.reshape(kernel(positions).T, X.shape)

    # Setup for plotting
    fig, ax = plt.subplots()
    plt.rc('font', size=10)
    plt.rc('xtick', labelsize=10)
    plt.rc('ytick', labelsize=10)

    title = "All Segments"
    filename = "All Segments"

    plotMultiColorOverlay(Z, title, xAxis, yAxis, xMax, xMin, yMax, yMin, dfList, filename, outputDir, seed)
    plotMultiColorContour(dfKde, title, xAxis, yAxis, xMax, xMin, yMax, yMin, dfList, filename, outputDir, seed)
    plt.close()
