import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import seaborn as sns
import configparser
from scipy import stats

# creates a randomized geometry grid for design
def getRandomGeometryGrid(numGeometries, ranges, xStarts, crossStarts):
    # create the output dataframe
    cols = 'xShift,crossingAngle,negAngle,axialRotation,negRot,zShift'.split(',')
    outputDf = pd.DataFrame(columns=cols)
    # get geometry range from ranges
    xShiftRange = ranges['xShift']
    crossingAngleRange = ranges['crossingAngle']
    axialRotationRange = ranges['axialRotation']
    zShiftRange = ranges['zShift']
    # loop through the xShifts and crossingAngles
    for xStart, cross in zip(xStarts, crossStarts):
        # define the xEnds and crossingAngleEnds
        xEnd = xStart + xShiftRange
        crossEnd = cross + crossingAngleRange
        # negative crossingAngle flag for design
        if (cross < 0):
            negAngle = 'false'
        else:
            negAngle = 'true'
        # loop through the number of geometries to get for each region
        for i in range(0,numGeometries):
            # get a random xShift, crossingAngle, axialRotation, and zShift
            xShift = round(rand.uniform(xStart, xEnd), 2)
            crossingAngle = round(rand.uniform(cross, crossEnd), 2)
            axialRotation = round(rand.uniform(0, axialRotationRange), 2)
            zShift = round(rand.uniform(0, zShiftRange), 2)
            # add these to the output dataframe
            outputDf = pd.concat([outputDf, pd.DataFrame([[xShift, crossingAngle, negAngle, axialRotation, 'true', zShift]], columns=cols)])
    return outputDf

# gets all of the possible points for a grid of geometries
def getSetGeometryGrid(ranges, increments, xStarts, crossStarts):
    cols = 'xShift,crossingAngle,negAngle,axialRotation,negRot,zShift,interface,sequence'.split(',')
    # get geometry range from ranges
    xShiftRange = ranges['xShift']
    crossingAngleRange = ranges['crossingAngle']
    axialRotationRange = ranges['axialRotation']
    zShiftRange = ranges['zShift']
    # get geometry increments from increments
    xInc = increments['xShift']
    crossInc = increments['crossingAngle']
    axInc = increments['axialRotation']
    zInc = increments['zShift']
    # loop through the xShifts and crossingAngles
    tmpDf = pd.DataFrame()
    for xStart, cross in zip(xStarts, crossStarts):
        # define the geometry ends
        # adjust ends: need to be higher to get the final desired increment
        xEnd = xStart + xShiftRange + xInc
        crossEnd = cross + crossingAngleRange + crossInc 
        axialEnd = axialRotationRange + axInc 
        zEnd = zShiftRange + zInc
        # negative crossingAngle flag for design
        if (cross < 0):
            negAngle = 'true'
            interface = '000110011001100110000'
            if (xStart < 8):
                sequence = 'LLLGALLGALLGALLGALILI'
            else:
                sequence = 'LLLAALLAALLAALLAALILI'
        else:
            negAngle = 'false'
            interface = '000011011001101100000'
            sequence = 'LLLLAALAALLAALAALLILI'
        # loop through geometries to get all values in grid
        xShiftList = np.arange(xStart, xEnd, xInc)
        crossingAngleList = abs(np.arange(cross, crossEnd, crossInc))
        axialRotationList = np.arange(0, axialEnd, axInc)
        zShiftList = np.arange(0, zEnd, zInc)
        # loop through the lists to get all combinations
        for xShift in xShiftList:
            x = round(xShift, 2)
            for crossingAngle in crossingAngleList:
                for axialRotation in axialRotationList:
                    for zShift in zShiftList:
                        adjustedAxRot = axialRotation+(20*zShift/3)
                        adjustedZShift = zShift+(0.015*axialRotation)
                        #print(axialRotation, adjustedAxRot, zShift, adjustedZShift)
                        tmpDf = pd.concat([tmpDf, pd.DataFrame([[x, crossingAngle, negAngle, adjustedAxRot, 'true', adjustedZShift, interface, sequence]], columns=cols)])
    return tmpDf

# Method to read config file settings
# Helper file for reading the config file of interest for running the program
def read_config(configFile):
    config = configparser.ConfigParser()
    config.read(configFile)
    return config

# get the configuration file for the current
def getConfigFile(configDir):
    configFile = ''
    # Access the configuration file for this program (should only be one in the directory)
    programDir = os.path.realpath(configDir)
    fileList = os.listdir(programDir)
    for file in fileList:
        fileName, fileExt = os.path.splitext(file)
        if fileExt == '.config':
            configFile = programDir + '/' + file
    if configFile == '':
        sys.exit("No config file present in script directory!")
    return configFile

# plot histogram of dataframe and column
def plotHist(df, column, outputDir, binList, title):
    # Plotting code below
    fig, ax = plt.subplots()
    # get the minimum and maximum values of the column
    ax.hist(df[column], weights=np.ones(len(df))/len(df), bins=binList, color='b')
    # set y axis to percent
    plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
    # set the y axis label
    plt.ylabel('Frequency')
    # set the x axis label
    plt.xlabel(title)
    # set the title
    plt.title(title+' histogram')
    # save the number of data points on the figure
    # get min and max of column
    min = df[column].min()
    plt.text(min-0.2, -0.05, 'n = '+str(len(df)))
    # save the figure
    plt.savefig(outputDir+"/histogram.png", bbox_inches='tight', dpi=150)
    plt.close()

def plotKde(df, xAxis, yAxis, xMin, xMax, xInc, yMin, yMax, yInc, outputDir, title):
    # grid the data for kde plots (split x into 20 bins, y into 12 bins)
    #X, Y = np.mgrid[xMin:xMax:20j, yMin:yMax:12j]
    X, Y = np.mgrid[xMin:xMax+xInc:xInc, yMin:yMax+yInc:yInc]
    # round all values to 2 decimal places
    X = np.around(X, 2)
    Y = np.around(Y, 2)
    x = df.loc[:, xAxis]
    y = df.loc[:, yAxis]

    #Kernel Density Estimate Calculation
    positions = np.vstack([X.ravel(), Y.ravel()])
    values = np.vstack([x, y])
    kernel = stats.gaussian_kde(values)
    kernel.set_bandwidth(bw_method='silverman')
    Z = np.reshape(kernel(positions).T, X.shape)

    outputTitle = xAxis+"_v_"+yAxis+"_"+title
    # Plotting code below
    fig, ax = plt.subplots()
    plt.grid(True)
    plt.xlabel(xAxis)
    plt.ylabel(yAxis)
    plt.title(title)
    ax.use_sticky_edges = False
    q = ax.imshow(np.rot90(Z), cmap=plt.cm.Blues,
        extent=[xMin, xMax, yMin, yMax], aspect="auto")
    x = df.loc[:, xAxis]
    y = df.loc[:, yAxis]
    #ax.plot(x, y, 'k.', markersize=10)
    ax.set_xlim([xMin, xMax])
    ax.set_ylim([yMin, yMax])
    axes = plt.gca()

    #plt.colorbar(q)
    # get min and max of column
    plt.text(xMin-0.2, yMin-0.5, 'n = '+str(len(df)))
    plt.savefig(outputDir+outputTitle+".png", bbox_inches='tight')
    #plt.show()

    sns.kdeplot(x=df[xAxis], y=df[yAxis], shade=False, cbar=True, cmap="inferno_r", levels = 10, thresh=False)

    # Extract kde and write into output file
    Z = kernel(positions).T

    # turn z into a percentage
    zMax = Z.max()
    Z = Z/zMax
    # round all values to 2 decimal places
    Z = np.around(Z, 2)
    # Output the density data for each geometry
    fid = open(outputDir+outputTitle+".csv",'w')
    #for currentIndex,elem in enumerate(positions):
    for currentIndex,elem in enumerate(Z):
        s1 = '%f, %f, %f\n'%(positions[0][currentIndex], positions[1][currentIndex], Z[currentIndex] )
        #s1 = '%f, %f, %f, %f, %f, %f, %f\n'%(positions[0][currentIndex], positions[1][currentIndex], positions[2][currentIndex], positions[3][currentIndex], positions[4][currentIndex], positions[5][currentIndex], Z[currentIndex]*10000000 )
        fid.write(s1)
    fid.close()