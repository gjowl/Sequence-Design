# -*- coding: utf-8 -*-
# @Author: Gilbert Loiseau
# @Date:   2021-9-13 18:37:30
# @Last Modified by:   Gilbert Loiseau
# @Last Modified time: 2022-04-22 15:39:24
"""
Created on Mon Sep 13 18:37:30 2021

This file contains a list of functions that are used in the following scripts:
    -analyzeDesignData.py
    -optimizedBackboneAnalysis.py
    -optimizeBackboneFunctions.py

@author: gjowl
"""

from datetime import date
from scipy import stats
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import logomaker as lm
from utilityFunctions import *

##############################################
#                 FUNCTIONS
##############################################
#Takes a set of sequences and compares them to another set of sequences, searching specifically for similarities with the interface
#def findSeq(interface):
#    for currSeq in seqList:
#        #iterate through currSeq to see if the combination is possible
#        for i in len(seq):
#            if seq[i] != -:
#                find

#def compareDesignAndPDBSequences(sequences):
#    #TODO: write in code to read in the sequences from my pdb dataset and compare to the sequences here
#    #1. read in teh sequences from my dataset
#    for seq in sequences:
#        findSeq(seqToCompare)
#    #2. setup a finder that will recognize any sequence similar (-can be anything but all the matching parts have to be the same)

def plotKde(df, xAxis, yAxis):
    #Variable set up depending on data that I'm running
    if xAxis == "Distance":
        xmin = 6
        xmax = 12
        ymin = -100
        ymax = 100
        X, Y = np.mgrid[xmin:xmax:24j, ymin:ymax:40j]
    elif xAxis == "Z1":
        xmin = 0
        xmax = 6
        ymin = 0
        ymax = 6
        X, Y = np.mgrid[xmin:xmax:24j, ymin:ymax:24j]
    elif xAxis == "Rot1":
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
    plt.grid(False)
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
    if xAxis == "Distance":
           ax.set_xticks([6,7,8,9,10,11,12])
    elif xAxis == "Rot1":
           ax.set_xticks([0,20,40,60,80,100])
    elif xAxis == "Z1":
           ax.set_xticks([0,1,2,3,4,5,6])
    axes = plt.gca()

    #save and show plot figure
    today = date.today()
    today = today.strftime("%Y_%m_%d")
    plt.colorbar(q)
    plt.savefig(today+"_"+xAxis+"_v_"+yAxis+".pdf", bbox_inches='tight')

    sns.kdeplot(df[xAxis], df[yAxis], shade=False, cbar=True, cmap="inferno_r", levels = 10, shade_lowest=False)

    # Extract kde and write into output file
    Z = kernel(positions).T

    # Output in date_xAxis_v_yAxis format

    #fid = open(today+"_"+xAxis+"_v_"+yAxis+"_kde_1.csv",'w')
    #for currentIndex,elem in enumerate(positions):
    for currentIndex,elem in enumerate(Z):
        s1 = '%f, %f, %f\n'%(positions[0][currentIndex], positions[1][currentIndex], Z[currentIndex] )
        #s1 = '%f, %f, %f, %f, %f, %f, %f\n'%(positions[0][currentIndex], positions[1][currentIndex], positions[2][currentIndex], positions[3][currentIndex], positions[4][currentIndex], positions[5][currentIndex], Z[currentIndex]*10000000 )
        #fid.write(s1)
    #fid.close()
    return Z

#Plotting Functions
#def plotOverlay(Z, xAxis, yAxis, xmax, xmin, ymax, ymin, xData, yData, outputDir):
#    # Plotting code below
#    fig, ax = plt.subplots()
#    plt.grid(True)
#    plt.xlabel(xAxis + " (Å)")
#    plt.ylabel(yAxis + " (°)")
#    plt.title('')
#    ax.use_sticky_edges = False
#    q = ax.imshow(np.rot90(Z), cmap=plt.cm.Blues,
#        extent=[xmin, xmax, ymin, ymax], aspect="auto")
#
#    # Plots the datapoints onto the graph
#    ax.plot(xData, yData, 'k.', markersize=1.33, color = "Red")
#    ax.set_xlim([xmin, xmax])
#    ax.set_ylim([ymin, ymax])
#    ax.set_xticks([6,7,8,9,10,11,12])
#    axes = plt.gca()
#
#    #save and show plot figure
#    today = date.today()
#    today = today.strftime("%Y_%m_%d")
#    plt.colorbar(q)
#    #plt.savefig(outputDir +xAxis+"_v_"+yAxis+".png", bbox_inches='tight', dpi=150)
#    plt.show()
#    plt.close()

def plotOverlay(Z, title, filename, xAxis, yAxis, xmax, xmin, ymax, ymin, xData, yData, outputDir):
    # Plotting code below
    fig, ax = plt.subplots()
    plt.grid(False)
    plt.xlabel(xAxis + " (Å)")
    plt.ylabel(yAxis + " (°)")
    plt.title(title)
    ax.use_sticky_edges = False
    q = ax.imshow(np.rot90(Z), cmap=plt.cm.Blues,
        extent=[xmin, xmax, ymin, ymax], aspect="auto")

    # Plots the datapoints onto the graph
    ax.plot(xData, yData, markersize=1.33, color = "Red")
    ax.set_xlim([xmin, xmax])
    ax.set_ylim([ymin, ymax])
    ax.set_xticks([6,7,8,9,10,11,12])
    axes = plt.gca()

    #save and show plot figure
    today = date.today()
    today = today.strftime("%Y_%m_%d")
    #plt.colorbar(q)
    plt.savefig(outputDir+filename+".png", bbox_inches='tight', dpi=150)
    plt.close()

def plotContour(df, title, filename, xAxis, yAxis, xmax, xmin, ymax, ymin, xData, yData, outputDir):
    figSNS, axSNS = plt.subplots()
    sns.kdeplot(x=df[xAxis], y=df[yAxis], shade=False, cbar=True, cmap="inferno_r", levels = 10, thresh=False, ax=axSNS)
    # Plots the datapoints onto the graph
    axSNS.set_xlim([xmin, xmax])
    axSNS.set_ylim([ymin, ymax])
    plt.xlabel(xAxis + " (Å)")
    plt.ylabel(yAxis + " (°)")
    plt.title(title)
    axSNS.plot(xData, yData, markersize=1.33, color = "Red")
    #plt.savefig(outputDir+xAxis+"_v_"+yAxis+"_contour.png", bbox_inches='tight', dpi=150)
    plt.savefig(outputDir+filename+"_contour.png", bbox_inches='tight', dpi=150)
    plt.close()

def plotKde(df, xAxis, yAxis, title, filename, outputDir):
    #Variable set up depending on data that I'm running
    xmin = 6
    xmax = 12
    ymin = -100
    ymax = 100
    X, Y = np.mgrid[xmin:xmax:24j, ymin:ymax:40j]
    x = df.loc[:, xAxis]
    y = df.loc[:, yAxis]

    #Kernel Density Estimate Calculation
    positions = np.vstack([X.ravel(), Y.ravel()])
    values = np.vstack([x, y])
    kernel = stats.gaussian_kde(values)
    kernel.set_bandwidth(bw_method='silverman')
    Z = np.reshape(kernel(positions).T, X.shape)

    # Setup for plotting code
    plt.rc('font', size=10)
    plt.rc('xtick', labelsize=10)
    plt.rc('ytick', labelsize=10)

    xData = df['xShift']
    yData = df['crossingAngle']
    plotOverlay(Z, title, filename, xAxis, yAxis, xmax, xmin, ymax, ymin, xData, yData, outputDir)
    plotContour(df, title, filename, xAxis, yAxis, xmax, xmin, ymax, ymin, xData, yData, outputDir)

    # Extract kde and write into output file
    Z = kernel(positions).T

    fid = open(outputDir+"_"+xAxis+"_v_"+yAxis+"_kde.csv",'w')
    for currentIndex,elem in enumerate(Z):
        s1 = '%f, %f, %f\n'%(positions[0][currentIndex], positions[1][currentIndex], Z[currentIndex] )
        fid.write(s1)
    fid.close()
    return Z

def plotDifferenceKde(df1, df2, xAxis, yAxis, title, filename, outputDir):
    #Variable set up depending on data that I'm running
    xmin = 6
    xmax = 12
    ymin = -100
    ymax = 100
    X, Y = np.mgrid[xmin:xmax:24j, ymin:ymax:40j]
    x1 = df1.loc[:, "Distance"]
    y1 = df1.loc[:, "Angle"]
    x2 = df2.loc[:, xAxis]
    y2 = df2.loc[:, yAxis]

    #Kernel Density Estimate Calculation
    positions = np.vstack([X.ravel(), Y.ravel()])
    values1 = np.vstack([x1, y1])
    values2 = np.vstack([x2, y2])
    kernel1 = stats.gaussian_kde(values1)
    kernel2 = stats.gaussian_kde(values2)
    kernel1.set_bandwidth(bw_method='silverman')
    kernel2.set_bandwidth(bw_method='silverman')
    Z1 = np.reshape(kernel1(positions).T, X.shape)
    Z2 = np.reshape(kernel2(positions).T, X.shape)


    #print(Z2)
    Z = Z2-Z1
    print(Z)
    #print(Z)
    # Setup for plotting code
    plt.rc('font', size=10)
    plt.rc('xtick', labelsize=10)
    plt.rc('ytick', labelsize=10)

    xData = df2['xShift']
    yData = df2['crossingAngle']
    plotOverlay(Z2, title, filename, xAxis, yAxis, xmax, xmin, ymax, ymin, xData, yData, outputDir)
    plotContour(df, title, filename, xAxis, yAxis, xmax, xmin, ymax, ymin, xData, yData, outputDir)

    # Extract kde and write into output file
    Z = kernel(positions).T

    fid = open(outputDir+"_"+xAxis+"_v_"+yAxis+"_kde.csv",'w')
    for currentIndex,elem in enumerate(Z):
        s1 = '%f, %f, %f\n'%(positions[0][currentIndex], positions[1][currentIndex], Z[currentIndex] )
        fid.write(s1)
    fid.close()
    return Z

def plotKdeOverlayForDfList(dfKde, listDf, dfNames, filenames, xAxis, yAxis, outputDir):
    #Variable set up depending on data that I'm running
    xmin = 6
    xmax = 12
    ymin = -100
    ymax = 100
    X, Y = np.mgrid[xmin:xmax:24j, ymin:ymax:40j]
    x = dfKde.loc[:, xAxis]
    y = dfKde.loc[:, yAxis]

    #Kernel Density Estimate Calculation
    positions = np.vstack([X.ravel(), Y.ravel()])
    values = np.vstack([x, y])
    kernel = stats.gaussian_kde(values)
    kernel.set_bandwidth(bw_method='silverman')
    Z = np.reshape(kernel(positions).T, X.shape)

    # Setup for plotting code
    plt.rc('font', size=10)
    plt.rc('xtick', labelsize=10)
    plt.rc('ytick', labelsize=10)

    i=0
    for df in listDf:
        xData = df['xShift']
        yData = df['crossingAngle']
        title = dfNames[i]
        filename = str(i)+"_"+filenames[i]
        plotOverlay(Z, title, filename, xAxis, yAxis, xmax, xmin, ymax, ymin, xData, yData, outputDir)
        plotContour(dfKde, title, filename, xAxis, yAxis, xmax, xmin, ymax, ymin, xData, yData, outputDir)
        i+=1

    # Extract kde and write into output file
    Z = kernel(positions).T

    fid = open(outputDir+"_"+xAxis+"_v_"+yAxis+"_kde.csv",'w')
    for currentIndex,elem in enumerate(Z):
        s1 = '%f, %f, %f\n'%(positions[0][currentIndex], positions[1][currentIndex], Z[currentIndex] )
        fid.write(s1)
    fid.close()
    return Z
#TODO: make this a bit more specific: take the counts for each AA, sum them, then determine the distribution from that distribution for each interface
def outputProbabilityDataframe(df, sheetName, writer):
    seqs = df["InterfaceSeq"]
    counts_mat = lm.alignment_to_matrix(sequences=seqs, to_type='counts', characters_to_ignore = '-')
    prob_mat = lm.transform_matrix(counts_mat, from_type='counts', to_type='probability')#can't use if want gaps between positions

    # Convert matrix to dataframe
    outputDf = pd.DataFrame(prob_mat)
    outputDf.to_excel(writer, sheetName)


# Sequence Logo Functions
def makeSeqLogo(df, title):
    seqs = df["InterfaceSeq"]
    counts_mat = lm.alignment_to_matrix(sequences=seqs, to_type='counts', characters_to_ignore = '-')
    #prob_mat = lm.transform_matrix(counts_mat, from_type='counts', to_type='probability')#can't use if want gaps between positions
    logo = lm.Logo(counts_mat, stack_order='small_on_top', color_scheme='skylign_protein')
    logo.ax.set_xlabel('Position')
    logo.ax.set_ylabel('Count')
    logo.ax.set_xlim([4, 17])
    logo.ax.set_xticks([4,5,6,7,8,9,10,11,12,13,14,15,16])
    plt.title(title)
    plt.close("all")

def getNumericColumns(df):
    columnNames = list(df.columns)
    dataRow = df.iloc[0]

    numericColumns = []
    for i in range(len(dataRow)):
        # Initialize array for numeric column names
        val = dataRow[i]
        currColumnName = columnNames[i]
        # try to convert string to float. If successful, add to numeric columns list
        try:
            float(val)
            numericColumns.append(currColumnName)
        except:
            print(currColumnName + " is not a numeric column")

    return numericColumns

# Converts the interface to -x- so that they can be compared
def convertInterfaceToX(df):
    interfaces = []
    for i, j in df.iterrows():
        interface = ""
        for AA in j["InterfaceSeq"][4:18]:
            if AA != "-":
                interface+="x"
            else:
                interface+="-"
        interfaces.append(interface)
    df["Interface"]=interfaces
    dataRow = df.iloc[0]

# Add dashes to the ends of the sequence since ends are constant
def removeInterfaceEnds(df):
    interfaces = []
    for i, j in df.iterrows():
        interface = ""
        for pos in range(len(j["InterfaceSeq"])):
            if pos < 4 or pos > 16:
                interface+="-"
            else:
                interface+=j["InterfaceSeq"][pos]
        interfaces.append(interface)
    df["InterfaceSeq"]=interfaces

def getBinNumber(energy, energyLimit, binSize, numberOfBins):
    binNumber = 0
    if energy < energyLimit:
        return binNumber
    else:
        while binNumber < numberOfBins:
            # define upper and lower energy bins
            upperBinLim = energyLimit+((binNumber+1)*binSize)
            lowerBinLim = energyLimit+(binNumber*binSize)
            if energy > lowerBinLim and energy < upperBinLim:
                binNumber+=1
                return binNumber
            else:
                binNumber+=1

# Add bin number
def addBinNumberColumn(df,energyLimit, binSize, numberOfBins):
    binColumn = []
    for i, j in df.iterrows():
        energy = j["Total"]
        binNumber = getBinNumber(energy, energyLimit, binSize, numberOfBins)
        binColumn.append(binNumber)
    df["Bin Number"] = binColumn

# TODO: I think I should bin these first, so then it's easier to look at the data
# Iterate through dataframe of all data and analyze sequences with same interfacial positions
# outputs a dataframe of that analyzed data and sequences logos for each interface (need to make this output more intuitive)
def interfaceAnalyzer(df, colNames, outputDir, writer):
    # Setup interface data dictionary
    interfaceDict = {}
    interfaceDict['Interface'] = []
    interfaceDict['Total'] = []
    interfaceDict['Number of Sequences'] = []
    interfaceDict['Number of Geometries'] = []
    interfaceDict['Highest Energy'] = []
    interfaceDict['Lowest Energy'] = []
    interfaceDict['Energy Range'] = []
    interfaceDict['xShift Range'] = []
    interfaceDict['CrossingAngle Range'] = []
    interfaceDict['axialRotation Range'] = []
    interfaceDict['zShift Range'] = []
    interfaceDict['angleDistDensity Range'] = []
    addColumnsToDictionary(interfaceDict, colNames)

    # get unique interfaces from the dataframe
    interfaceDf = df.groupby('Interface').head(1)

    # Iterate through the interfaces and analyze the data for each unique interface
    for i, j in interfaceDf.iterrows():
        interface = j['Interface']
        tmpDf = df[df['Interface'] == interface]
        #makeSeqLogo(tmpDf, interface)
        getColumnAverages(tmpDf, colNames, interfaceDict)

        interfaceDict['Interface'].append(interface)
        interfaceDict['Number of Sequences'].append(len(tmpDf))
        interfaceDict['Number of Geometries'].append(tmpDf['crossingAngle'].nunique())
        interfaceDict['Highest Energy'].append(tmpDf['Total'].max())
        interfaceDict['Lowest Energy'].append(tmpDf['Total'].min())
        interfaceDict['Energy Range'].append(tmpDf['Total'].min()-tmpDf['Total'].max())
        interfaceDict['xShift Range'].append(tmpDf['xShift'].max()-tmpDf['xShift'].min())
        interfaceDict['CrossingAngle Range'].append(tmpDf['crossingAngle'].max()-tmpDf['crossingAngle'].min())
        interfaceDict['axialRotation Range'].append(tmpDf['axialRotation'].max()-tmpDf['axialRotation'].min())
        interfaceDict['zShift Range'].append(tmpDf['zShift'].max()-tmpDf['zShift'].min())
        interfaceDict['angleDistDensity Range'].append(tmpDf['angleDistDensity'].max()-tmpDf['angleDistDensity'].min())

    # Convert dictionary to dataframe
    outputDf = pd.DataFrame.from_dict(interfaceDict)
    sheetName = "Interface Summary"
    outFile = outputDir + 'SequenceInterfaceAnalysisSummary.xlsx'
    newWriter = pd.ExcelWriter(outFile)
    writeDataframeToSpreadsheet(outputDf, newWriter, sheetName)
    newWriter.save()
    newWriter.close()

def getAACount(seqList, AA, dict):
    AAcount = 0
    for seq in seqList:
        for pos in range(len(seq)):
            if AA == seq[pos]:
                AAcount+=1
    dict[AA].append(AAcount)

def getSeqProbability(AA, dict):
    AAcount = 0
    for pos in range(len(seq)):
        if AA == seq[pos]:
            AAcount+=1
    dict[AA].append(AAcount)

def getDfInterfaceCount(df, dfToAnalyze, writer):
    # Setup interface data dictionary
    dictInterface = {}
    dictInterface['Interface'] = []

    # TODO: add in a list of AAs used that gets autogenerated from the config file and put in here
    listAA = ["A", "F", "G", "I", "L", "S", "T", "V", "W", "Y"]
    addColumnsToDictionary(dictInterface, listAA)

    # Iterate through the interfaces and analyze the data for each unique interface
    for i, j in dfToAnalyze.iterrows():
        interface = j['Interface']
        tmpDf = df[df['Interface'] == interface]

        # append to dictionary
        dictInterface['Interface'].append(interface)

        # get list of interfaces and count each AA
        seqList = tmpDf["InterfaceSeq"]
        for AA in listAA:
            getAACount(seqList, AA, dictInterface)

        #writeDataframeToSpreadsheet(tmpDf, writer, interface)

    # Convert dictionary to dataframe
    outputDf = pd.DataFrame.from_dict(dictInterface)
    #total = outputDf.iloc[:, 1:].sum(axis=1)
    #tmpDf = outputDf.iloc[:, 1:].div(total, axis=0)
    interfaceColumn = outputDf["Interface"]
    writeDataframeToSpreadsheet(outputDf, writer, "InterfaceProbability")
    return outputDf, interfaceColumn

def getDfInterfaceProbability(df, dfToAnalyze, writer):
    # Setup interface data dictionary
    dictInterface = {}
    dictInterface['Interface'] = []

    # TODO: add in a list of AAs used that gets autogenerated from the config file and put in here
    listAA = ["A", "F", "G", "I", "L", "S", "T", "V", "W", "Y"]
    addColumnsToDictionary(dictInterface, listAA)

    # Iterate through the interfaces and analyze the data for each unique interface
    for i, j in dfToAnalyze.iterrows():
        interface = j['Interface']
        tmpDf = df[df['Interface'] == interface]

        # get list of interfaces
        seqList = tmpDf["InterfaceSeq"]
        for AA in listAA:
            getAACount(seqList, AA, dictInterface)

        # append to dictionary
        dictInterface['Interface'].append(interface)
        #writeDataframeToSpreadsheet(tmpDf, writer, interface)

    # Convert dictionary to dataframe
    outputDf = pd.DataFrame.from_dict(dictInterface)
    writeDataframeToSpreadsheet(outputDf, writer, "InterfaceAATotals")
    total = outputDf.iloc[:, 1:].sum(axis=1)
    tmpDf = outputDf.iloc[:, 1:].div(total, axis=0)
    dfInterfaceProb = tmpDf.copy()#I think these are references???
    interfaceColumn = outputDf["Interface"]
    #outputDf.insert(0, 'Interface', outputDf['Interface'])
    outputDf['Total'] = total
    writeDataframeToSpreadsheet(dfInterfaceProb, writer, "InterfaceProbability")
    #sheetName = 'InterfaceProbability'
    #writeDataframeToSpreadsheet(newDf, writer, sheetName)
    return dfInterfaceProb, interfaceColumn

def getDfMembraneProbability(dfInterfaceProb, dfMembraneSequenceProb, writer):
    dictMembraneProb = {}
    #dictMembraneProb['Interface'] = []

    # TODO: add in a list of AAs used that gets autogenerated from the config file and put in here
    listAA = ["A", "F", "G", "I", "L", "S", "T", "V", "W", "Y"]
    addColumnsToDictionary(dictMembraneProb, listAA)

    # Convert to dictionary
    # Transforms numpy.array() of values in each columns into dictionary (key = value column1, value = value column2)
    dictSeqProb = dict(dfMembraneSequenceProb.values)
    for i in range(len(dfInterfaceProb)):
        for AA in listAA:
            interfaceProb = dfInterfaceProb[AA][i]
            if interfaceProb != 0:
                membraneProb = dictSeqProb.get(AA)
                dictMembraneProb[AA].append(membraneProb)
            else:
                dictMembraneProb[AA].append(0)
    #sheetName = 'InterfaceProbability'
    #writeDataframeToSpreadsheet(newDf, writer, sheetName)
    #writer.save()
    #writer.close()

    dfMembraneProb = pd.DataFrame.from_dict(dictMembraneProb)
    total = dfMembraneProb.sum(axis=1)
    tmpDf = dfMembraneProb.div(total, axis=0)
    dfMembraneProb = tmpDf.copy()
    #tmpDf.insert(0, 'Interface', outputDf['Interface'])
    #dfMembraneProb.insert(0, 'Interface', dfInterfaceProb['Interface'])
    sheetName = 'MembraneSequenceProbability'
    writeDataframeToSpreadsheet(dfMembraneProb, writer, sheetName)

    return dfMembraneProb

#TODO: organize this code and think of a way to split these into bins...can I output things into output bin folders?
def interfaceSequenceCounts(df, dfSeqProb, colNames, outputDir, writer):
    # get unique interfaces from the dataframe
    dfInterface = df.groupby('Interface').head(1)

    sheetName = 'Interfaces'
    outFile = outputDir + 'SequenceInterfaceAnalysis.xlsx'
    interfaceWriter = pd.ExcelWriter(outFile)
    writeDataframeToSpreadsheet(dfInterface, interfaceWriter, sheetName)
    dfInterfaceCount, interfaceColumn = getDfInterfaceCount(df, dfInterface, interfaceWriter)
    #dfMembraneProb = getDfMembraneProbability(dfInterfaceProb, dfSeqProb, interfaceWriter)

    #dfSubtract = dfInterfaceProb-dfMembraneProb
    #dfDivide = dfSubtract.div(dfMembraneProb)*100
    dfInterfaceCount['Interface Number'] = dfInterfaceCount.reset_index().index
    #dfSubtract.insert(0, 'Interface', interfaceColumn)
    sheetName2 = 'Interface Count'
    writeDataframeToSpreadsheet(dfInterfaceCount, interfaceWriter, sheetName2)
#
    #total = dfDivide.sum(axis=1)
    #max_val = np.max(total)
    #total = total/max_val
#
    #sheetName3 = 'Divide by Membrane Probability'
    #dfDivide['Normalized Difference'] = total
    #writeDataframeToSpreadsheet(dfDivide, interfaceWriter, sheetName3)
    interfaceWriter.save()
    interfaceWriter.close()

def interfaceSequenceAnalyzer(df, dfSeqProb, colNames, outputDir, writer):
    # get unique interfaces from the dataframe
    dfInterface = df.groupby('Interface').head(1)

    sheetName = 'Interfaces'
    outFile = outputDir + 'SequenceInterfaceAnalysis.xlsx'
    interfaceWriter = pd.ExcelWriter(outFile)
    writeDataframeToSpreadsheet(dfInterface, interfaceWriter, sheetName)
    dfInterfaceProb, interfaceColumn = getDfInterfaceProbability(df, dfInterface, interfaceWriter)
    dfMembraneProb = getDfMembraneProbability(dfInterfaceProb, dfSeqProb, interfaceWriter)

    dfSubtract = dfInterfaceProb-dfMembraneProb
    dfDivide = dfSubtract.div(dfMembraneProb)*100
    dfSubtract['Interface Number'] = dfSubtract.reset_index().index
    dfSubtract.insert(0, 'Interface', interfaceColumn)
    sheetName2 = 'Interface-Membrane'
    writeDataframeToSpreadsheet(dfSubtract, interfaceWriter, sheetName2)

    total = dfDivide.sum(axis=1)
    max_val = np.max(total)
    total = total/max_val

    sheetName3 = 'Divide by Membrane Probability'
    dfDivide['Normalized Difference'] = total
    writeDataframeToSpreadsheet(dfDivide, interfaceWriter, sheetName3)
    interfaceWriter.save()
    interfaceWriter.close()

def analyzeSequencesWithSameInterface(df, columnsToAnalyze, writer):
    convertInterfaceToX(df)
    removeInterfaceEnds(df)
    interfaceAnalyzer(df, columnsToAnalyze, writer)

def outputFileIntoBinFolder(df, interfaceNumber, binNumber, binNames, sheetName, outputDir):
    binOutputDir = outputDir + "Interface_" + str(interfaceNumber) + "\\"
    if not os.path.isdir(binOutputDir):
        print('Creating output directory: ' + binOutputDir + '.')
        os.mkdir(binOutputDir)
        #print('Output Directory: ' + outputDir + ' exists.')
    outFile = binOutputDir + binNames[binNumber] + ".xlsx"
    writer = pd.ExcelWriter(outFile)
    writeDataframeToSpreadsheet(df, writer, sheetName)
    writer.save()
    writer.close()

def outputProbabilityDataframeInterface(df, interface, binNumber):
    seqs = df["InterfaceSeq"]
    counts_mat = lm.alignment_to_matrix(sequences=seqs, to_type='counts', characters_to_ignore = '-')
    prob_mat = lm.transform_matrix(counts_mat, from_type='counts', to_type='probability')#can't use if want gaps between positions

    # Convert matrix to dataframe
    outputDf = pd.DataFrame(prob_mat)
    outputDf.to_excel(writer, sheetName)

# use in a for loop with dataframes for every interface
def binAndAverageInterfaces(df, numberOfBins, outputDir):
    #bins = ['-30','-30to-25','-25to-20','-20to-15','-15to-10','-10to-5']
    bins = ['-30','-30to-25','-25to-20','-20to-15','-15to-10','-10to-5','-5to0','0to5','5to10']
    # read in unique sequence dataframe
    interfaceFile = outputDir + 'SequenceInterfaceAnalysis.xlsx'
    #interfaceSheet = 'Interface-Membrane'
    interfaceSheet = 'Interface Count'
    interfaceDf = pd.read_excel(interfaceFile, sheet_name=interfaceSheet)
    # Iterate through the interfaces and analyze the data for each unique interface
    for i, j in interfaceDf.iterrows():
        interface = j['Interface']
        interfaceNumber = j['Interface Number']
        dfInterface = df[df['Interface'] == interface]
        bin=0
        while bin < numberOfBins:
            tmpDf = dfInterface[dfInterface["Bin Number"] == bin]
            if len(tmpDf) > 0:
                outputFileIntoBinFolder(tmpDf, interfaceNumber, bin, bins, interface, outputDir)
            bin+=1

# TODO: make this more general so I can add it to utilities
# Analyzes data from a datafram in bins
# what are different ways you could bin by?
# def analyzeBinnedData(df, binName, binRule, numberOfBins, columnNames, outputDir, outFile):
def binAndAverage(df, numberOfBins, binName, columnNames, sheetName, writer):
    i=0
    dictAvg = {}
    dictAvg['Number of Sequences'] = []
    dictAvg['Number of Geometries'] = []
    #bins = ['x < -30','-30<x<-25','-25<x<-20','-20<x<-15','-15<x<-10','-10<x<-5']
    bins = ['x < -30','-30<x<-25','-25<x<-20','-20<x<-15','-15<x<-10','-10<x<-5','-5<x<0','0<x<5','5<x<10' ]
    addColumnsToDictionary(dictAvg, columnNames)
    while i < numberOfBins:
        tmpDf = df[df["Bin Number"] == i]
        getColumnAverages(tmpDf, columnNames, dictAvg)
        numSequences = len(tmpDf)
        dictAvg['Number of Sequences'].append(numSequences)
        dictAvg['Number of Geometries'].append(tmpDf['crossingAngle'].nunique())
        #if (numSequences != 0):
            #outputProbabilityDataframe(tmpDf, bins[i], writer)
        i+=1

    outputDf = pd.DataFrame.from_dict(dictAvg)
    outputDf.index = bins
    outputDf.to_excel(writer, sheetName)

def analyzeDataframe(df, numberOfBins, binName, columnNames, sheetNames, writer):
    # Separate into left vs right handed dimers
    dfLeft = df[df["crossingAngle"] > 0]
    dfRight = df[df["crossingAngle"] < 0]

    # output dataframes into spreadsheet
    writeDataframeToSpreadsheet(dfLeft, writer, "Left Handed")
    writeDataframeToSpreadsheet(dfRight, writer, "Right Handed")

    # Get averages for dataframes
    binAndAverage(df, numberOfBins, binName, columnNames, sheetNames[0], writer)
    #binAndAverage(dfLeft, numberOfBins, binName, columnNames, sheetNames[1], writer)
    #binAndAverage(dfRight, numberOfBins, binName, columnNames, sheetNames[2], writer)

# Interfacial Analysis Functions
def getInterfaceCount(df):
    count = []
    for i, j in df.iterrows():
        interfaceCount = 0
        for AA in j["InterfaceSeq"][3:18]:
            if AA != "-":
                interfaceCount+=1
        count.append(interfaceCount)
    df.loc[:,"InterfaceCount"] = count

def getInterfaceLeuCount(df):
    count = []
    for i, j in df.iterrows():
        interfaceCount = 0
        for AA in j["InterfaceSeq"][3:18]:
            if AA == "L":
                interfaceCount+=1
        count.append(interfaceCount)
    df.loc[:, "InterfaceLeuCount"] = count

def ridOfSequencesWithLessThanXInterfacials(df, numInterface):
    outputDf = pd.DataFrame()
    getInterfaceCount(df)
    getInterfaceLeuCount(df)
    #outputDf = df[df["InterfaceCount"]-df["InterfaceLeuCount"] >= numInterface]
    outputDf = df[df["InterfaceLeuCount"] <= numInterface]
    return outputDf

def calcSeqProbabilityComparison(outputDir, seqProbDf):
    # load Sequence Probability File to compare
    fileName = outputDir + "SequenceInterfaceAnalysis.xlsx"
    dfToAnalyze = pd.read_excel(fileName, sep=",")

    # Convert to dictionary
    seqProbDict = dfToAnalyze.to_dict()

    # Iterate through columns and write down the difference score
    dictOutputSeqProb = {}
    dictOutputSeqProb['Total Probability'] = []
    aaList = dfToAnalyze.columns
    for i, j in seqProbDf.iterrows():
        totSeqProb = 0
        for pos in range(len(aaList)):
            AA = aaList[i]
            numAA = j[AA]
            if numAA > 0:
                aaProb = dictSeqProb.get(AA)
                outputDictSeqProb[AA].append(aaProb)
                totSeqProb+=aaProb
        dictOutputSeqProb['Total Probability'].append(totSeqProb)

    outputDf = pd.DataFrame.from_dict(dictOutputSeqProb)
    newWriter = pd.ExcelWriter(outputDir + 'OutputProb.xlsx')
    writeDataframeToSpreadsheet(outputDf, newWriter, sheetName)
    newWriter.save()
    newWriter.close()

#returns an int
def getNumberOfSequences(df):
    return df['Sequence'].nunique()

def getNumberOfGeometries(df):
    return df['crossingAngle'].nunique()

def outputDataframeComparison(listDf, dfNames, outputDir):
    dict = {}
    dict['Number of Sequences'] = []
    dict['Number of Geometries'] = []
    dict['Average Density'] = []
    for i in range(len(listDf)):
        df = listDf[i]
        dict['Number of Sequences'].append(df['Sequence'].nunique())
        dict['Number of Geometries'].append(df['crossingAngle'].nunique())
        dict['Average Density'].append(df['angleDistDensity'].mean()*10)

    outputDf = pd.DataFrame.from_dict(dict)
    outputDf.index = dfNames
    sheetName = 'Summary'
    writer = pd.ExcelWriter(outputDir + 'DataTrimmingSummary.xlsx')
    writeDataframeToSpreadsheet(outputDf, writer, sheetName)
    writer.save()
    writer.close()

def plotHistogramsForDfList(listDf, binList, colorList, listDfTitle, listFilenames, colName, outputDir):
    #TODO: should I just add these as defaults to the rc file?
    plt.rc('font', size=40)
    plt.rc('xtick', labelsize=30)
    plt.rc('ytick', labelsize=30)
    i=0
    #TODO: think of a way to integrate labels into here
    for df in listDf:
        tmpDf = df[df[colName] < 100]
        #tmpDf.hist(column=colName, bins=10, figsize=(25,25), color=colorList[i])
        tmpDf.hist(column=colName, bins=binList, figsize=(25,25), color='purple')
        #tmpDf.hist(column=colName, bins=np.arange(max(tmpDf[colName]), max(tmpDf[colName])+binwidth, binwidth), figsize=(25,25), color='purple')
        title = listDfTitle[i]
        filename = listFilenames[i]
        plt.title(title)
        plt.savefig(outputDir+str(i)+"_"+filename+"_"+colName+".png", bbox_inches='tight', dpi=150)
        i+=1

#TODO: fix this code to get multiple plots on the same plot
def plotDfvsDf(df1, df2, colName):
    fig, ax = plt.subplots()
    adjustTotal1 = df1.loc[:, colName].sum()
    adjustTotal2 = df2.loc[:, colName].sum()
    a_heights, a_bins = np.histogram(df1[colName]/adjustTotal1)
    b_heights, b_bins = np.histogram(df2[colName]/adjustTotal2, bins=a_bins)

    width = (a_bins[1] - a_bins[0])/3

    ax.bar(a_bins[:-1], a_heights, width=width, facecolor='cornflowerblue')
    ax.bar(b_bins[:-1]+width, b_heights, width=width, facecolor='seagreen')

def getAADistribution(df, listAA, outputDir, name):
    outFile = outputDir + name + '.xlsx'
    #outFile = outputDir + '2021_12_3_SequencesFromMembraneAnalysisAADistributionCheck.xlsx'
    writer = pd.ExcelWriter(outFile)
    dictAA = {}
    addColumnsToDictionary(dictAA, listAA)
    #df = df[df["DesignNumber"] > 0]
    seqList = df["InterfaceSeq"]
    for AA in listAA:
        getAACount(seqList, AA, dictAA)
    print(dictAA)
    outputDf = pd.DataFrame.from_dict(dictAA)
    outputDf["Total"] = outputDf.sum(axis=1)
    totalAAs = outputDf.iloc[0]["Total"]
    newRow = outputDf.div(totalAAs)
    outputDf = outputDf.append(newRow, ignore_index=True)
    writeDataframeToSpreadsheet(outputDf, writer, 'AATotals')
    writer.save()
    writer.close()

def writeConfigurationFile(df, fileName):
    designPDBList = df["PDBPath"]
    with open(fileName, "w+") as variableFile:
        for i in designPDBList:
            designDir = i[:-26]#TODO: make this better; it currently just gets up to the 26th character to get the dir
            repackConfig = designDir+"/repack.config\n"
            variableFile.write(designDir + "," + repackConfig)
        print("Variable File written: ", fileName)


def getTrimmedDataframe(df, columnName, columnLimit, lessThan):
    newDf = pd.DataFrame()
    if lessThan is True:
        newDf = df[df[columnName] < columnLimit]
    else:
        newDf = df[df[columnName] > columnLimit]
    seqTotal = getNumberOfSequences(newDf)
    geomTotal = getNumberOfGeometries(newDf)
    print(columnName + " < " + str(columnLimit) + "\n#Sequences: " + str(seqTotal) + "\n#Geometries: " + str(geomTotal))
    return newDf
