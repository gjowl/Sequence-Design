import pandas as pd
import sys
import os
import numpy as np
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt
import matplotlib.colors
from scipy import stats
import seaborn as sns
import logomaker

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
    #df['VDWDiff'] = df['VDWDimerBBOptimize'] - df['VDWMonomer']
    #df['HBONDDiff'] = df['HBONDDimerBBOptimize'] - df['HBONDMonomer']
    #df['IMM1Diff'] = df['IMM1DimerBBOptimize'] - df['IMM1Monomer']
    #df['VDWRepackDiff'] = df['VDWDimerBBOptimize'] - df['VDWDimerPreBBOptimize']
    #df['HBONDRepackDiff'] = df['HBONDDimerBBOptimize'] - df['HBONDDimerPreBBOptimize']
    #df['IMM1RepackDiff'] = df['IMM1DimerBBOptimize'] - df['IMM1DimerPreBBOptimize']
    #df['RepackChange'] = df['Total'] - df['TotalPreBBOptimize']
    #df['EntropyChange'] = df['currEntropy'] - df['prevEntropy']
    #df['SASADiff'] = df['BBOptimizeSasa'] - df['MonomerSasa']
    df['VDWDiff'] = df['VDWDimerOptimize'] - df['VDWMonomer']
    df['HBONDDiff'] = df['HBONDDimerOptimize'] - df['HBONDMonomer']
    df['IMM1Diff'] = df['IMM1DimerOptimize'] - df['IMM1Monomer']
    df['VDWRepackDiff'] = df['VDWDimerOptimize'] - df['VDWDimerPreOptimize']
    df['HBONDRepackDiff'] = df['HBONDDimerOptimize'] - df['HBONDDimerPreOptimize']
    df['IMM1RepackDiff'] = df['IMM1DimerOptimize'] - df['IMM1DimerPreOptimize']
    df['RepackChange'] = df['Total'] - df['TotalPreOptimize']
    #df['EntropyChange'] = df['currEntropy'] - df['prevEntropy']
    df['SasaDiff'] = df['OptimizeSasa'] - df['MonomerSasa']
    return df

def getGeomChanges(df):
    # add in dimer vs monomer energy difference
    df['AxChange'] = df['endAxialRotationPrime'] - df['startAxialRotationPrime']
    df['xChange'] = df['endXShift'] - df['startXShift']
    df['crossChange'] = df['endCrossingAngle'] - df['startCrossingAngle']
    df['zChange'] = df['endZShiftPrime'] - df['startZShiftPrime']
    return df

def plotMeanAndSDBarGraph(df, dir, xAxis, yAxis):
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
    plt.savefig(dir+'/'+xAxis+'_'+yAxis+'_barGraph.png')
    plt.close()

def plotEnergyDiffs(df, outputDir, outputName):
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
    fig.savefig(outputDir+'/energyDiffPlot_'+outputName+'.png')
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
    # get min and max of the data rounded to the nearest 5
    minData = int(np.floor(np.min(data)/5)*5)
    maxData = int(np.ceil(np.max(data)/5)*5)
    # flip the data so that the min is at the top of the colorbar
    norm = matplotlib.colors.Normalize(vmin=minData, vmax=maxData) 
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

# loop through the region dataframes
def addGeometricDistanceToDataframe(df, outputDir, geomList):
    outputDf = pd.DataFrame()
    for region in df['Region'].unique():
        tmpDf = df[df['Region'] == region].copy()
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
        tmpDf.to_csv(dir+'/geometricDistance.csv', index=False)
        # concatenate the dataframes
        outputDf = pd.concat([outputDf, tmpDf])
    return outputDf 

def plotScatterMatrix(df, outputDir):
    cols = ['xShift_dist', 'crossingAngle_dist', 'axialRotationPrime_dist', 'zShiftPrime_dist']
    # trim the dataframe to only the columns of interest
    tmpDf = df[cols]
    # rename the columns to be more readable by removing _dist
    tmpDf.columns = ['xShift', 'crossingAngle', 'axialRotation', 'zShift']
    pd.plotting.scatter_matrix(tmpDf, alpha=0.2, figsize=(6, 6))
    # add a trendline to the plot
    sns.pairplot(tmpDf, kind="reg")
    # add the correlation coefficient and r-squared to each plot
    for i, j in zip(*np.triu_indices_from(tmpDf, 1)):
        ax = plt.subplot(4, 4, i * 4 + j + 1)
        ax.text(0.05, 0.9, 'r = {:.2f}'.format(tmpDf.iloc[:, i].corr(tmpDf.iloc[:, j])), transform=ax.transAxes, fontsize=10)
        ax.text(0.05, 0.8, 'r-squared = {:.2f}'.format(tmpDf.iloc[:, i].corr(tmpDf.iloc[:, j])**2), transform=ax.transAxes, fontsize=10)
    plt.savefig(outputDir+'/scatterMatrix.png', bbox_inches='tight', dpi=150)
    plt.close()

def getMeanAndSDDf(df, colNames):
    tmpDf = pd.DataFrame()
    for col in colNames:
        mean, sd = df[col].mean(), df[col].std()
        tmpDf = pd.merge(tmpDf, pd.DataFrame({col: [mean], col+'SD': [sd]}), how='outer', left_index=True, right_index=True)
    return tmpDf

def getAAPercentageComposition(df, percentCompositionFile, listAA, seqColumn, outputDir):
    # get the percentage composition of each amino acid in the sequence
    # read in the AA sequence composition data with columns: AA, Entropy
    mergedCountsDf = pd.read_csv(percentCompositionFile, sep=',', header=0)
    # loop through dataframe regions
    for region in df['Region'].unique():
        tmpDf = df[df['Region'] == region]
        # make a dictionary of amino acids
        aaDict = {}
        for aa in listAA:
            aaDict[aa] = 0
        for index, row in tmpDf.iterrows():
            for aa in listAA:
                # count the number of times each amino acid appears in the interface
                aaDict[aa] += row[seqColumn].count(aa)
        # make a dataframe of the amino acid dictionary with columns for AA and count
        tmpDf = pd.DataFrame.from_dict(aaDict, orient='index')
        tmpDf = tmpDf.reset_index()
        tmpDf.columns = ['AA', 'Count']
        # sum the total number of amino acids
        tmpDf['Total'] = tmpDf['Count'].sum()
        # get the percentage of each amino acid by dividing the count by the total
        tmpDf[region] = tmpDf['Count'] / tmpDf['Total']
        # add the region AA percentage to a merged dataframe
        mergedCountsDf = pd.merge(mergedCountsDf, tmpDf[['AA', region]], on='AA')
    # output the merged dataframe
    mergedCountsDf.to_csv(outputDir+'/aaPercentagesByRegion.csv', index=False)
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

def getEnergyDifferenceDf(df, columns, numSeqs):
    # loop through each region
    outputDf = pd.DataFrame()
    for region in df['Region'].unique():
        # get the dataframe for the region
        tmpDf = df[df['Region'] == region]
        # sort the df by energy
        tmpDf = tmpDf.sort_values(by=['Total'])
        # only keep the top numSeqs
        tmpDf = tmpDf.head(numSeqs)
        # get the mean and standard deviation for each column
        tmpDf = getMeanAndSDDf(tmpDf, columns)
        # merge the region column
        tmpDf = pd.merge(tmpDf, pd.DataFrame({'Region': [region]}), how='outer', left_index=True, right_index=True)
        # concat the tmpDf to the outputDf
        outputDf = pd.concat([outputDf, tmpDf], axis=0, ignore_index=True)
    return outputDf

def scatter3DWithColorbar(df, xAxis, yAxis, zAxis, colorbar, outputDir, name):
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    x, y, z, a = df[xAxis], df[yAxis], df[zAxis], df[colorbar]
    sc = ax.scatter(x, y, z, c=a, cmap='viridis', linewidth=0.5)
    # set labels and title
    ax.set_xlabel(xAxis, fontweight='bold')
    ax.set_ylabel(yAxis, fontweight='bold')
    ax.set_zlabel(zAxis, fontweight='bold')
    ax.set_title('3D Scatter Plot')
    # move colorbar to the side of the z label
    cbar = plt.colorbar(sc, pad=0.2, shrink=0.5, aspect=15)
    # add a label to the colorbar
    plt.clabel(colorbar)
    # save plot
    plt.savefig(outputDir+'/3DScatter_'+name+'.png')
    plt.close()

def getInterfaceSequence(df):
    outputDf = pd.DataFrame()
    for region in df['Region'].unique():
        tmpDf = df[df['Region'] == region].copy()
        interfaceSeqList = []
        for interface,seq in zip(tmpDf['Interface'], tmpDf['Sequence']):
            # loop through the interface and keep only the amino acids that are in the interface
            interfaceSeq = ''
            for i in range(len(str(interface))):
                if str(interface)[i] == '1':
                    interfaceSeq += seq[i]
            interfaceSeqList.append(interfaceSeq)
        tmpDf['InterfaceSeq'] = interfaceSeqList
        # concatenate the dataframes
        outputDf = pd.concat([outputDf, tmpDf])
    return outputDf

# TODO: fix this function so that it's easier to make more plots 
def makePlotsForDataframe(df, df_kde, outputDir, name, barGraphCols, energyList):
    # loop through each geometryNumber
    xCol = 'replicateNumber'
    for col in barGraphCols:
        plotMeanAndSDBarGraph(df, outputDir, xCol, col)
    plotScatterMatrix(df, outputDir)
    # set the below up to look at just the regions, not the whole geom
    for energy in energyList:
        plotGeomKde(df_kde, df, energy, outputDir, 'xShift', 'crossingAngle')
    # shift the names of the geometry columns to be the same as the geomList
    x, y, z, c = 'xShift', 'crossingAngle', 'zShift', 'axialRotation'
    scatter3DWithColorbar(df, x, y, z, c, outputDir, name)
    makeInterfaceSeqLogo(df, outputDir)

def makeInterfaceSeqLogo(df, outputDir):
    '''This function will make a logo of the interface sequence'''
    # get the interface sequences
    sequences = df['Sequence']
    # get the interface
    interfaces = df['Interface']
    # loop through the interface and keep only the amino acids that are in the interface
    interfaceSequences = []
    for interface in interfaces: 
        for seq in sequences:
            # loop through each position in the interface
            for j in range(len(str(interface))):
                if str(interface)[j] == '0':
                    # replace the amino acid with a dash if it is not in the interface (if 0 at that position)
                    seq = seq[:j] + '-' + seq[j+1:]
            interfaceSequences.append(seq)
    # use logomaker to make the logo
    mat = logomaker.alignment_to_matrix(interfaceSequences, to_type='counts') #TODO: find a way to convert to percentages without aas at non-interface positions on the logo
    logo = logomaker.Logo(mat, color_scheme='hydrophobicity')
    logo.ax.xaxis.set_ticks_position('none')
    logo.style_spines(spines=['left', 'right'], visible=False)
    # make a list for the xticks for the sequence length
    xticks = []
    for i in range(1, len(interfaceSequences[0])+1):
        xticks.append(i)
    logo.ax.set_xticks(xticks)

    # save the logo
    logo.fig.savefig(outputDir + '/interfaceSeqLogo.png')
    # close the logo
    plt.close()