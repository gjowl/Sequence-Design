import pandas as pd
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors
from scipy import stats

def setupOutputDir(inputFile):
    '''
        This function creates the output directory for the analysis.
    '''
    # get directory of the input file
    inputDir = os.path.dirname(inputFile)
    if inputDir == '':
        inputDir = os.getcwd()

    # make output directory named after the input file
    outputDir = inputDir + '/' + os.path.basename(inputFile).split('.')[0]
    # check if the analysis directory exists
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)
    return outputDir

def getRepackEnergies(df):
    # add in dimer vs monomer energy difference
    df['VDWDiff'] = df['VDWDimerBBOptimize'] - df['VDWMonomer']
    df['HBONDDiff'] = df['HBONDDimerBBOptimize'] - df['HBONDMonomer']
    df['IMM1Diff'] = df['IMM1DimerBBOptimize'] - df['IMM1Monomer']
    df['VDWRepackDiff'] = df['VDWDimerBBOptimize'] - df['VDWDimerPreBBOptimize']
    df['HBONDRepackDiff'] = df['HBONDDimerBBOptimize'] - df['HBONDDimerPreBBOptimize']
    df['IMM1RepackDiff'] = df['IMM1DimerBBOptimize'] - df['IMM1DimerPreBBOptimize']
    df['RepackChange'] = df['Total'] - df['TotalPreBBOptimize']
    df['EntropyChange'] = df['currEntropy'] - df['prevEntropy']
    df['SASADiff'] = df['BBOptimizeSasa'] - df['MonomerSasa']
    return df

def getGeomChanges(df):
    # add in dimer vs monomer energy difference
    df['AxChange'] = df['endAxialRotationPrime'] - df['startAxialRotationPrime']
    df['xChange'] = df['endXShift'] - df['startXShift']
    df['crossChange'] = df['endCrossingAngle'] - df['startCrossingAngle']
    df['zChange'] = df['endZShiftPrime'] - df['startZShiftPrime']
    return df

def plotMeanAndSDBarGraph(df, outputDir, xAxis, yAxis):
    df_avg = df.groupby(xAxis)[yAxis].mean().reset_index()
    # plot the mean and standard deviation of the repack change for each geometry number on a bar graph using matplotlib
    fig, ax = plt.subplots()
    ax.bar(df_avg[xAxis], df_avg[yAxis], yerr=df.groupby(xAxis)[yAxis].std().reset_index()[yAxis])
    ax.set_xlabel(xAxis)
    ax.set_ylabel(yAxis)
    ax.set_title('Average '+yAxis+' for '+xAxis)
    # set x axis to be integers
    ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
    plt.savefig(outputDir+'/avgRepackChange.png')
    plt.close()

def plotEnergyDiffs(df, outputDir):
    # data columns to plot
    n = len(df)
    x = np.arange(n)*3
    #numBars = len(energyList)
    numBars = 5
    width = 1/numBars
    #fig, ax = plt.subplots()
    #for energy in energyList:
    #    energy = df[energy]
    #    p = plt.bar(x, height)
    # get the VDW energy difference column
    VDWDiff = df['VDWDiff']
    # get the HBOND energy difference column
    HBONDDiff = df['HBONDDiff']
    # get the IMM1 energy difference column
    IMM1Diff = df['IMM1Diff']
    total = df['Total']
    entropy = df['Entropy']
    sasa = df['SASADiff']
    # setup the bar plots for each energy difference
    fig, ax = plt.subplots()
    # plot the VDW energy difference with standard deviation
    #ax.bar(x, VDWDiff, width, color='cornflowerblue', edgecolor='black', yerr=df['sdVDW'], label='VDW')
    #ax.bar(x, VDWDiff, width, yerr=df['VDWRepackDiff'].std(), label='VDW')
    p1 = plt.bar(x-width*2, VDWDiff, width, yerr=df['sdVDW'], color='cornflowerblue', edgecolor='black')
    # plot the HBOND energy difference adjacent to the VDW energy difference
    p2 = plt.bar(x-width, HBONDDiff, width, yerr=df['sdHBOND'], color='lightcoral', edgecolor='black')
    p3 = plt.bar(x, IMM1Diff, width, yerr=df['sdIMM1'],color='palegreen', edgecolor='black')
    p4 = plt.bar(x+width, total, width, yerr=df['sdTotal'],color='thistle', edgecolor='black')
    p5 = plt.bar(x+width*2, entropy, width, yerr=df['sdEntropy'],color='blanchedalmond', edgecolor='black')
    #p6 = plt.bar(x+width*3, entropy, width, yerr=df['sdSASA'],color='azure', edgecolor='black')
    # change the dpi to make the image smaller
    fig.set_dpi(2000)
    plt.ylabel('Energy')
    plt.title('Energy Plot')
    plt.legend((p1[0], p2[0], p3[0], p4[0], p5[0]), ('VDW', 'HBOND', 'IMM1', 'Total', 'Entropy'))
    # set x axis labels as regions
    plt.xticks(x, df['Region'])
    fig.savefig(outputDir+'/energyDiffPlot.png')
    plt.close()

def plotGeomKde(df_kde, df_data, dataColumn, outputDir, xAxis, yAxis, region):
    # read in kde file from command line, or default to 2020_09_23_kdeData.csv
    #df_data = df_data.drop_duplicates('crossingAngle',keep='first')

    # get the x and y axes data to be plotted from the dataframe
    x = df_data.loc[:, xAxis]
    y = df_data.loc[:, yAxis]
    energies = df_data[dataColumn].values

    # get the kde plot for the geometry data
    kdeZScores = getKdePlotZScoresplotKdeOverlayForDfList(df_kde, 'Distance', 'Angle')

    # plot the kde plot with an overlay of the input dataset   
    plotKdeOverlay(kdeZScores, x, y, energies, dataColumn, outputDir, region)

def plotKdeOverlay(kdeZScores, xAxis, yAxis, data, dataColumn, outputDir, region):
    # Plotting code below
    fig, ax = plt.subplots()
    # plotting labels and variables 
    plt.grid(False)
    plt.xlabel("Distance (Å)")
    plt.ylabel("Angle (°)")
    plt.title(dataColumn)
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
    min_val = np.min(data)
    max_val = np.max(data)
    # flip the data so that the min is at the top of the colorbar
    norm = matplotlib.colors.Normalize(vmin=-55, vmax=-5) # TODO: change this to the min and max of the data
    ax.scatter(xAxis, yAxis, c=cmap(norm(data)), s=30, alpha=0.5)
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
    plt.text(xmin-1, ymax+7, "# Geometries = " + str(len(xAxis)), fontsize=10)
    ax.set_xlim([xmin, xmax])
    ax.set_ylim([ymin, ymax])
    ax.set_xticks([6,7,8,9,10,11,12])
    axes = plt.gca()

    #plt.colorbar(q)
    # output the number of sequences in the dataset onto plot
    plt.savefig(outputDir+"/kdeOverlay_"+region+".png", bbox_inches='tight', dpi=150)
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

# loop through the region dataframes
def addGeometricDistanceToDataframe(df_list, outputDir):
    geomDfList = []
    for df in df_list:
        tmpDf = df.copy()
        # normalize the xShift, crossing angle, axialRotation, and zShift data using min-max normalization
        tmpDf['normStartXShift'] = (tmpDf['startXShift'] - tmpDf['startXShift'].min()) / (tmpDf['startXShift'].max() - tmpDf['startXShift'].min())
        tmpDf['normStartCrossingAngle'] = (tmpDf['startCrossingAngle'] - tmpDf['startCrossingAngle'].min()) / (tmpDf['startCrossingAngle'].max() - tmpDf['startCrossingAngle'].min())
        tmpDf['normStartAxialRotation'] = (tmpDf['startAxialRotationPrime'] - tmpDf['startAxialRotationPrime'].min()) / (tmpDf['startAxialRotationPrime'].max() - tmpDf['startAxialRotationPrime'].min())
        tmpDf['normStartZShift'] = (tmpDf['startZShiftPrime'] - tmpDf['startZShiftPrime'].min()) / (tmpDf['startZShiftPrime'].max() - tmpDf['startZShiftPrime'].min())
        # normalize the end xShift, crossing angle, axialRotation, and zShift data using min-max normalization
        tmpDf['normEndXShift'] = (tmpDf['endXShift'] - tmpDf['startXShift'].min()) / (tmpDf['startXShift'].max() - tmpDf['startXShift'].min())
        tmpDf['normEndCrossingAngle'] = (tmpDf['endCrossingAngle'] - tmpDf['startCrossingAngle'].min()) / (tmpDf['startCrossingAngle'].max() - tmpDf['startCrossingAngle'].min())
        tmpDf['normEndAxialRotation'] = (tmpDf['endAxialRotationPrime'] - tmpDf['startAxialRotationPrime'].min()) / (tmpDf['startAxialRotationPrime'].max() - tmpDf['startAxialRotationPrime'].min())
        tmpDf['normEndZShift'] = (tmpDf['endZShiftPrime'] - tmpDf['startZShiftPrime'].min()) / (tmpDf['startZShiftPrime'].max() - tmpDf['startZShiftPrime'].min())
        # calculate the distance between the start and end points for each geometry
        tmpDf['xDist'] = np.sqrt((tmpDf['normEndXShift'] - tmpDf['normStartXShift'])**2)
        tmpDf['crossDist'] = np.sqrt((tmpDf['normEndCrossingAngle'] - tmpDf['normStartCrossingAngle'])**2)
        tmpDf['axialDist'] = np.sqrt((tmpDf['normEndAxialRotation'] - tmpDf['normStartAxialRotation'])**2)
        tmpDf['zDist'] = np.sqrt((tmpDf['normEndZShift'] - tmpDf['normStartZShift'])**2)
        # calculate the total distance between the start and end points for each geometry
        tmpDf['GeometricDistance'] = np.sqrt((tmpDf['normStartXShift'] - tmpDf['normEndXShift'])**2 + (tmpDf['normStartCrossingAngle'] - tmpDf['normEndCrossingAngle'])**2 + (tmpDf['normStartAxialRotation'] - tmpDf['normEndAxialRotation'])**2 + (tmpDf['normStartZShift'] - tmpDf['normEndZShift'])**2)
        region = tmpDf['Region'].iloc[0]
        # output the dataframe to a csv file
        tmpDf.to_csv(outputDir+'/'+region+'_geometricDistance.csv')
        # append to the list of dataframes
        geomDfList.append(tmpDf)
        # make a 4x4 scatterplot of the start and end points
        plt.scatter(tmpDf['xDist'], tmpDf['crossDist'], s=5, alpha=0.5)
        plt.savefig(outputDir+'/'+region+'_crossXgeometricDistance.png', bbox_inches='tight', dpi=150)
        plt.close()
        plt.scatter(tmpDf['axialDist'], tmpDf['zDist'], s=5, alpha=0.5)
        # output the plot
        plt.savefig(outputDir+'/'+region+'_axZgeometricDistance.png', bbox_inches='tight', dpi=150)
        plt.close()
    return geomDfList