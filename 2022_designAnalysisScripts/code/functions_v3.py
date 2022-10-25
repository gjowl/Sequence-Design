import pandas as pd
import sys
import os
import numpy as np
from sklearn.metrics import r2_score
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

def plotMeanAndSDBarGraph(df, outputFile, xAxis, yAxis):
    df_avg = df.groupby(xAxis)[yAxis].mean().reset_index()
    # plot the mean and standard deviation of the repack change for each geometry number on a bar graph using matplotlib
    fig, ax = plt.subplots()
    # get the standard deviation of the repack change for each geometry number
    ax.bar(df_avg[xAxis], df_avg[yAxis], yerr=df.groupby(xAxis)[yAxis].std().reset_index()[yAxis])
    ax.set_xlabel(xAxis)
    ax.set_ylabel(yAxis)
    ax.set_title('Average '+yAxis+' for '+xAxis)
    # set x axis to be integers
    ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
    plt.savefig(outputFile)
    plt.close()

def plotEnergyDiffs(df, outputDir):
    # data columns to plot
    n = len(df)
    x = np.arange(n)*3
    numBars = 4
    width = 1/numBars
    # get the VDW energy difference column
    VDWDiff = df['VDWDiff']
    # get the HBOND energy difference column
    HBONDDiff = df['HBONDDiff']
    # get the IMM1 energy difference column
    IMM1Diff = df['IMM1Diff']
    total = df['Total']
    # setup the bar plots for each energy difference
    fig, ax = plt.subplots()
    # plot the energy differences with standard deviation
    p1 = plt.bar(x-width*2, VDWDiff, width, yerr=df['VDWDiffSD'], color='cornflowerblue', edgecolor='black')
    p2 = plt.bar(x-width, HBONDDiff, width, yerr=df['HBONDDiffSD'], color='lightcoral', edgecolor='black')
    p3 = plt.bar(x, IMM1Diff, width, yerr=df['IMM1DiffSD'],color='palegreen', edgecolor='black')
    p4 = plt.bar(x+width, total, width, yerr=df['TotalSD'],color='thistle', edgecolor='black')
    # change the dpi to make the image smaller
    fig.set_dpi(2000)
    plt.ylabel('Energy')
    plt.title('Energy Plot')
    # add legend with the legend to the right of the plot
    plt.legend((p1[0], p2[0], p3[0], p4[0]), ('VDW', 'HBOND', 'IMM1', 'Total'), loc='center left', bbox_to_anchor=(1.0, 0.5))
    # set size so that the legend fits
    plt.gcf().set_size_inches(12, 5)
    # set x axis labels as regions
    plt.xticks(x, df['Region'])
    fig.savefig(outputDir+'/energyDiffPlot.png')
    plt.close()

#def plotEnergyDiffs(df, outputDir, enerColumns):
#    # keep only the energy columns from the df
#    tmpDf = df[enerColumns]
#    # plot the energy differences
#    df.plot(kind='bar', yerr=tmpDf.std(), title='Energy Differences', figsize=(10,10))
#    plt.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
#    # add in y-axis label
#    plt.ylabel('Percent')
#    plt.savefig(outputDir+'/energyDiffs.png')
#    plt.close()

def plotGeomKde(df_kde, df_data, dataColumn, outputDir, xAxis, yAxis):
    # get the x and y axes data to be plotted from the dataframe
    x = df_data.loc[:, xAxis]
    y = df_data.loc[:, yAxis]
    energies = df_data[dataColumn].values
    region = df_data['Region'].values[0]
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
    plt.title(region)
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
    ax.set_xlim([xmin, xmax])
    ax.set_ylim([ymin, ymax])
    ax.set_xticks([6,7,8,9,10,11,12])
    axes = plt.gca()

    # output the number of sequences in the dataset onto plot
    plt.savefig(outputDir+"/kdeOverlay.png", bbox_inches='tight', dpi=150)
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
def addGeometricDistanceToDataframe(df_list, outputDir, geomList):
    geomDfList = []
    for df in df_list:
        tmpDf = df.copy()
        distList = []
        for geom in geomList:
            # capitalize the first letter of the geometry
            tmpGeom = geom[0].upper() + geom[1:]
            # add start and end to the geometry name
            startGeom, endGeom = "start" + tmpGeom, "end" + tmpGeom
            # min denominator
            denominator = df[startGeom].max() - df[startGeom].min()
            startNumerator, endNumerator = (df[startGeom] - df[startGeom].min()), (df[endGeom] - df[startGeom].min())
            # calculate the normalized distance for the geometry
            normStart, normEnd = startNumerator / denominator, endNumerator / denominator
            # save the normalized distance to the dataframe
            normStartCol, normEndCol = startGeom + '_norm', endGeom + '_norm'
            tmpDf[normStartCol], tmpDf[normEndCol] = normStart, normEnd
            # distance calculation
            dist = (tmpDf[normEndCol] - tmpDf[normStartCol])
            distCol = geom + '_dist'
            tmpDf[distCol] = np.sqrt(dist**2)
            distList.append(dist**2)
        # calculate the min-max normalized distance for the geometry
        tmpDf['GeometricDistance'] = np.sqrt(np.sum(distList, axis=0))
        region = tmpDf['Region'].iloc[0]
        # output the dataframe to a csv file
        dir = outputDir + '/' + region
        # make a directory for each region
        if not os.path.exists(dir):
            os.makedirs(dir)
        tmpDf.to_csv(dir+'/geometricDistance.csv')
        # append to the list of dataframes
        geomDfList.append(tmpDf)
        # make a 4x4 scatterplot of the start and end points
        plt.scatter(tmpDf['xShift_dist'], tmpDf['crossingAngle_dist'], s=5, alpha=0.5)
        # add title and labels
        plt.title(region)
        plt.xlabel("xShift")
        plt.ylabel("crossingAngle")
        # get a trendline for the data
        z = np.polyfit(tmpDf['xShift_dist'], tmpDf['crossingAngle_dist'], 1)
        p = np.poly1d(z)
        plt.plot(tmpDf['xShift_dist'],p(tmpDf['xShift_dist']),"r--")
        # output the equation of the trendline and the r-squared value
        plt.text(0.1, -0.1, "y=%.6fx+(%.6f)"%(z[0],z[1]), ha='center', va='center', transform=plt.gca().transAxes)
        plt.text(0.1, -0.2, "r-squared=%.6f"%(r2_score(tmpDf['xShift_dist'], tmpDf['crossingAngle_dist'])), ha='center', va='center', transform=plt.gca().transAxes)
        plt.savefig(dir+'/crossXgeometricDistance.png', bbox_inches='tight', dpi=150)
        plt.close()
        plt.scatter(tmpDf['axialRotationPrime_dist'], tmpDf['zShiftPrime_dist'], s=5, alpha=0.5)
        # get a trendline for the data
        z = np.polyfit(tmpDf['axialRotationPrime_dist'], tmpDf['zShiftPrime_dist'], 1)
        p = np.poly1d(z)
        plt.plot(tmpDf['axialRotationPrime_dist'],p(tmpDf['axialRotationPrime_dist']),"r--")
        # output the equation of the trendline next to the line
        plt.text(0.1, -0.1, 'y=%.6fx+(%.6f)'%(z[0],z[1]), ha='center', va='center', transform=plt.gca().transAxes)
        plt.text(0.1, -0.2, "r-squared=%.6f"%(r2_score(tmpDf['axialRotationPrime_dist'], tmpDf['zShiftPrime_dist'])), ha='center', va='center', transform=plt.gca().transAxes)
        # add title and labels
        plt.title(region)
        plt.xlabel("axialRotation")
        plt.ylabel("zShift")
        # output the plot
        plt.savefig(dir+'/axZgeometricDistance.png', bbox_inches='tight', dpi=150)
        plt.close()
    return geomDfList

def getMeanAndSDDf(df, colNames):
    tmpDf = pd.DataFrame()
    for col in colNames:
        mean, sd = df[col].mean(), df[col].std()
        tmpDf = pd.merge(tmpDf, pd.DataFrame({col: [mean], col+'SD': [sd]}), how='outer', left_index=True, right_index=True)
    return tmpDf

def getAAPercentageComposition(df_list, percentCompositionFile, listAA, seqColumn, outputDir):
    # get the percentage composition of each amino acid in the sequence
    # read in the AA sequence composition data with columns: AA, Entropy
    mergedCountsDf = pd.read_csv(percentCompositionFile, sep=',', header=0)
    # loop through dataframe regions
    for df in df_list:
        # make a dictionary of amino acids
        aaDict = {}
        for aa in listAA:
            aaDict[aa] = 0
        for index, row in df.iterrows():
            for aa in listAA:
                # count the number of times each amino acid appears in the interface
                aaDict[aa] += row[seqColumn].count(aa)
        # make a dataframe of the amino acid dictionary with columns for AA and count
        tmpDf = pd.DataFrame.from_dict(aaDict, orient='index')
        tmpDf = tmpDf.reset_index()
        tmpDf.columns = ['AA', 'Count']
        # sum the total number of amino acids
        tmpDf['Total'] = tmpDf['Count'].sum()
        region = df['Region'].iloc[0]
        # get the percentage of each amino acid by dividing the count by the total
        tmpDf[region] = tmpDf['Count'] / tmpDf['Total']
        # add the region AA percentage to a merged dataframe
        mergedCountsDf = pd.merge(mergedCountsDf, tmpDf[['AA', region]], on='AA')
    # output the merged dataframe
    mergedCountsDf.to_csv(outputDir+'/aaPercentagesByRegion.csv')
    # plot the AA percentages for each region in a bar chart with different colors
    mergedCountsDf.plot.bar(x='AA', rot=0, color=['royalblue', 'firebrick', 'cornsilk', 'lightsalmon'], edgecolor='black')
    # set the plot size
    plt.gcf().set_size_inches(12, 5)
    plt.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
    plt.title('Amino Acid Percent Composition Per region')
    # add in y-axis label
    plt.ylabel('Percent')
    plt.savefig(outputDir+'/AApercentages_'+seqColumn+'.png')
    plt.close()