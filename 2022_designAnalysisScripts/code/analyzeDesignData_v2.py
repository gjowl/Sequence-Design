import pandas as pd
import sys
import os
import numpy as np
from plotGeomKde import *
from functions import *
import matplotlib.pyplot as plt


'''
    This file is used to analyze the data from my second set of design runs after CHIP1.
    The goal of this analysis is to determine if this data is better than my previous runs
    by outputting graphs and statistics to a csv file. I can then compare those graphs and
    data to the previous design runs from CHIP1, aiming to have an expectation for the fluorescence
    output depending on the energies, geometry, and sequence of the protein.
'''

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

def plotMeanAndSDBarGraph(df, xAxis, yAxis):
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

# Read in the data from the csv file
df = pd.read_csv(sys.argv[1], sep=',', header=0)
kdeFile = os.getcwd()+'/' + '2020_09_23_kdeData.csv'

# read in kde data as a dataframe
df_kde = pd.read_csv(kdeFile)

# Set up output directory
outputDir = setupOutputDir(sys.argv[1])

# rid of anything with Total > 0 and repack energy > 0
df = df[df['Total'] < -10]
df = df[df['VDWDimer'] < 0]

# only keep the unique sequence with best total energy
df = df.sort_values(by=['Total'], ascending=True)
df = df.drop_duplicates(subset=['Sequence'], keep='first')

# loop through dataframe rows
for index, row in df.iterrows():
    # check the xShift value
    if row['startXShift'] <= 7.5:
        # add region column GAS
        df.loc[index, 'Region'] = 'GAS'
    elif row['startXShift'] > 7.5 and row['startCrossingAngle'] < 0:
        # add region column GAS
        df.loc[index, 'Region'] = 'Right'
    elif row['startXShift'] > 7.5 and row['startCrossingAngle'] > 0:
        # add region column Left
        df.loc[index, 'Region'] = 'Left'

# sort by total energy
df = df.sort_values(by=['Total'])
df.to_csv(outputDir+'/allData.csv')

# get the top 100 sequences in Total Energy for each region
df_GAS = df[df['Region'] == 'GAS']
df_Left = df[df['Region'] == 'Left']
df_Right = df[df['Region'] == 'Right']

# add region dataframes to a list
df_list = [df_GAS, df_Left, df_Right]

# loop through the region dataframes
for df in df_list:
    # normalize the xShift, crossing angle, axialRotation, and zShift data using min-max normalization
    df['xShift'] = (df['startXShift'] - df['startXShift'].min()) / (df['startXShift'].max() - df['startXShift'].min())
    df['crossingAngle'] = (df['startCrossingAngle'] - df['startCrossingAngle'].min()) / (df['startCrossingAngle'].max() - df['startCrossingAngle'].min())
    df['axialRotation'] = (df['startAxialRotation'] - df['startAxialRotation'].min()) / (df['startAxialRotation'].max() - df['startAxialRotation'].min())
    df['zShift'] = (df['startZShift'] - df['startZShift'].min()) / (df['startZShift'].max() - df['startZShift'].min())
    # normalize the end xShift, crossing angle, axialRotation, and zShift data using min-max normalization
    df['endXShift'] = (df['endXShift'] - df['startXShift'].min()) / (df['startXShift'].max() - df['startXShift'].min())
    df['endCrossingAngle'] = (df['endCrossingAngle'] - df['startCrossingAngle'].min()) / (df['startCrossingAngle'].max() - df['startCrossingAngle'].min())
    df['endAxialRotation'] = (df['endAxialRotation'] - df['startAxialRotation'].min()) / (df['startAxialRotation'].max() - df['startAxialRotation'].min())
    df['endZShift'] = (df['endZShift'] - df['startZShift'].min()) / (df['startZShift'].max() - df['startZShift'].min())
    # calculate the distance between the start and end points
    df['normStartEndDistance'] = np.sqrt((df['normStartXShift'] - df['normEndXShift'])**2 + (df['normStartCrossingAngle'] - df['normEndCrossingAngle'])**2 + (df['normStartAxialRotation'] - df['normEndAxialRotation'])**2 + (df['normStartZShift'] - df['normEndZShift'])**2)
    # output the dataframe to a csv file
    df.to_csv(outputDir+'/normalizedData.csv')

exit(0)

# get the top 100 sequences in Total Energy for each region
df_GAS = df[df['Region'] == 'GAS'].head(10)
df_Left = df[df['Region'] == 'Left'].head(10)
df_Right = df[df['Region'] == 'Right'].head(10)

# add region dataframes to a list
df_list = [df_GAS, df_Left, df_Right]

# output the dataframes to csv files
for i in range(len(df_list)):
    df_list[i].to_csv(outputDir+'/top10_'+df_list[i]['Region'].iloc[0]+'.csv')

df_avg = pd.DataFrame()
# loop through the region dataframes
for df in df_list:
    tmpDf = getRepackEnergies(df)
    tmpDf = getGeomChanges(tmpDf)
    # get region name
    region = df['Region'].iloc[0]
    # get average VDWDiff, HBONDDiff, and IMM1Diff from the top 100 sequences
    avgVDWDiff, sdVDW = tmpDf['VDWDiff'].mean(), tmpDf['VDWDiff'].std()
    avgHBONDDiff, sdHBOND = tmpDf['HBONDDiff'].mean(), tmpDf['HBONDDiff'].std()
    avgIMM1Diff, sdIMM1 = tmpDf['IMM1Diff'].mean(), tmpDf['IMM1Diff'].std()
    avgEntropy, sdEntropy = tmpDf['EntropyChange'].mean(), tmpDf['EntropyChange'].std()
    avgTotal, sdTotal = tmpDf['Total'].mean(), tmpDf['Total'].std()
    avgSasa, sdSasa = tmpDf['SASADiff'].mean(), tmpDf['SASADiff'].std()
    # add the region and average VDWDiff, HBONDDiff, IMM1Diff, and Total to dataframe using concat
    df_avg = pd.concat([df_avg, pd.DataFrame({'Region': [region], 'VDWDiff': [avgVDWDiff], 'sdVDW': [sdVDW], 'HBONDDiff': [avgHBONDDiff], 'sdHBOND': [sdHBOND], 'IMM1Diff': [avgIMM1Diff], 'sdIMM1': [sdIMM1], 'Entropy': [avgEntropy], 'sdEntropy': [sdEntropy], 'Total': [avgTotal], 'sdTotal': [sdTotal], 'SASADiff': [avgSasa], 'sdSASA': [sdSasa]})], ignore_index=True)
    #df_avg = pd.concat([df_avg, pd.DataFrame({'Region': [region], 'VDWDiff': [avgVDWDiff], 'sdVDW': [sdVDW], 'HBONDDiff': [avgHBONDDiff], 'sdHBOND': [sdHBOND], 'IMM1Diff': [avgIMM1Diff], 'sdIMM1': [sdIMM1], 'Entropy': [avgEntropy], 'sdEntropy': [sdEntropy], 'Total': [avgTotal], 'sdTotal': [sdTotal]})])
    #df_avg = pd.concat([df_avg, pd.DataFrame({'Region': [region], 'VDWDiff': [avgVDWDiff], 'sdVDW': [sdVDW], 'HBONDDiff': [avgHBONDDiff], 'sdHBOND': [sdHBOND], 'IMM1Diff': [avgIMM1Diff], 'sdIMM1': [sdIMM1], 'Total': [avgTotal], 'sdTotal': [sdTotal]})])
    plotGeomKde(df_kde, df, 'Total', outputDir, 'startXShift', 'startCrossingAngle', region)
    plotHist(df, 'Total',outputDir, region)

print(df_avg)
plotMeanAndSDBarGraph(df, 'geometryNumber', 'VDWDiff')
plotEnergyDiffs(df_avg, outputDir)
exit()
# output the top 100 sequences to a csv file
df_top.to_csv(outputDir+'/top100.csv')

# sort the dataframes by vdwDiff plus hbondDiff using loc
df = df.sort_values(by=['VDWDiff', 'HBONDDiff'])

# the below works, but try to think of a better way to plot it to make it more visually appealing and easier to understand
plotEnergyDiffStackedBarGraph(df,outputDir)

# sort by total energy
df = df.sort_values(by=['Total'])

# output the data to a csv file
df.to_csv(outputDir+"/data.csv")

# ideas for analysis
"""
    - compare geometries from duplicate sequences
    - compare geometries from non-duplicate sequences (kde plots for this and above?)\
    - scatterplots of predicted fluorescence...?
    - overlay of kde plots for CHIP1 vs now; maybe overlay of geometries that worked in CHIP1
    - bar graph of each of the terms with mean total energy for the top 100 sequences for each region
"""
