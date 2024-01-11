"""
Created on Mon Sep 13 18:37:30 2021

@author: gjowl
"""
"""
This file is contains all of the functions for analysis of my design runs for use in 2021_11_02_designAnalyzer
"""
from datetime import date
from scipy import stats
from matplotlib import gridspec
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import re
import seaborn as sns
import logomaker as lm
from utility import *

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

def compareDesignAndPDBSequences(sequences):
    #TODO: write in code to read in the sequences from my pdb dataset and compare to the sequences here
    #1. read in teh sequences from my dataset
    for seq in sequences:
        findSeq(seqToCompare)
    #2. setup a finder that will recognize any sequence similar (-can be anything but all the matching parts have to be the same)

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
    plt.show()

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
def plotKdeOverlay(dfKde, xData, yData, xAxis, yAxis, type, outDir):
    #Variable set up depending on data that I'm running
    if xAxis == "xShift":
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
    x = dfKde.loc[:, xAxis]
    y = dfKde.loc[:, yAxis]

    if type == 1:
        name = "Negative"
    if type == 2:
        name = "PositiveVDW"
    if type == 3:
        name = "Clashing"
    if type == 4:
        name = "all"
    if type == 5:
        name = "DimerNoIMM1"
    if type == 6:
        name = "21Neg"
    if type == 7:
        name = "24Neg"
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
    plt.title(xAxis+"_v_"+yAxis+"_"+name)
    ax.use_sticky_edges = False
    q = ax.imshow(np.rot90(Z), cmap=plt.cm.Blues,
        extent=[xmin, xmax, ymin, ymax], aspect="auto")
    ax.plot(xData, yData, 'k.', markersize=3, color = "Red")
    x = dfKde.loc[:, xAxis]
    y = dfKde.loc[:, yAxis]
    #ax.plot(x, y, 'k.', markersize=2)
    #ax.margins(x=2, y=2)
    ax.set_xlim([xmin, xmax])
    ax.set_ylim([ymin, ymax])
    #ax.set_aspect(0.5)
    if xAxis == "xShift":
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
    plt.savefig(today+"_"+xAxis+"_v_"+yAxis+"_"+name+".png", bbox_inches='tight')

    figSNS, axSNS = plt.subplots()
    plt.title(xAxis+"_v_"+yAxis+"_"+name)
    if xAxis == "Distance":
        sns.kdeplot(dfKde[xAxis], dfKde[yAxis], shade=False, cbar=True, cmap="inferno_r", levels = 5, shade_lowest=False, ax=axSNS)
    else:
        sns.kdeplot(dfKde[xAxis], dfKde[yAxis], shade=False, cbar=True, cmap="inferno_r", levels = 10, shade_lowest=False, ax=axSNS)
    axSNS.plot(xData, yData, 'k.', markersize=3, color = "Blue")
    plt.savefig(today+"_"+xAxis+"_v_"+yAxis+"_"+name+"_contour.png", bbox_inches='tight')
    plt.close()
    # Extract kde and write into output file
    Z = kernel(positions).T

    # Output in date_xAxis_v_yAxis format

    fid = open(outDir+today+"_"+xAxis+"_v_"+yAxis+"_kde.csv",'w')
    #for currentIndex,elem in enumerate(positions):
    for currentIndex,elem in enumerate(Z):
        s1 = '%f, %f, %f\n'%(positions[0][currentIndex], positions[1][currentIndex], Z[currentIndex] )
        #s1 = '%f, %f, %f, %f, %f, %f, %f\n'%(positions[0][currentIndex], positions[1][currentIndex], positions[2][currentIndex], positions[3][currentIndex], positions[4][currentIndex], positions[5][currentIndex], Z[currentIndex]*10000000 )
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
    plt.show()
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

def interfaceSequenceAnalyzer(df, dfSeqProb, colNames, outputDir, writer):
    # Setup interface data dictionary
    interfaceDict = {}
    interfaceDict['Interface'] = []

    # TODO: add in a list of AAs used that gets autogenerated from the config file and put in here
    aaList = ["A", "F", "G", "I", "L", "S", "T", "V", "W", "Y"]
    addColumnsToDictionary(interfaceDict, aaList)

    # get unique interfaces from the dataframe
    interfaceDf = df.groupby('Interface').head(1)

    outFile = outputDir + 'InterfaceData.xlsx'
    sheetName = 'Interfaces'
    interfaceWriter = pd.ExcelWriter(outFile)
    writeDataframeToSpreadsheet(interfaceDf, interfaceWriter, sheetName)
    # Iterate through the interfaces and analyze the data for each unique interface
    for i, j in interfaceDf.iterrows():
        interface = j['Interface']
        tmpDf = df[df['Interface'] == interface]

        seqList = tmpDf["InterfaceSeq"]
        for AA in aaList:
            getAACount(seqList, AA, interfaceDict)

        interfaceDict['Interface'].append(interface)
        writeDataframeToSpreadsheet(tmpDf, interfaceWriter, interface)

    # Convert dictionary to dataframe
    outputDf = pd.DataFrame.from_dict(interfaceDict)
    total = outputDf.iloc[:, 1:].sum(axis=1)
    newDf = outputDf.iloc[:, 1:].div(total, axis=0)
    dfToSubtract1 = newDf.copy()#I think these are references???

    newDf.insert(0, 'Interface', outputDf['Interface'])
    total = newDf.iloc[:, 1:].sum(axis=1)
    newDf['Total'] = total
    outputDf.to_excel(writer, "Interface Data")
    newDf.to_excel(writer, "Interface New Data")

    #TODO: make into separate function
    outFile = outputDir + 'SequenceInterfaceAnalysis.xlsx'
    newWriter = pd.ExcelWriter(outFile)
    # Setup interface dict 2
    inter2 = {}
    addColumnsToDictionary(inter2, aaList)

    # Convert to dictionary
    # Transforms numpy.array() of values in each columns into dictionary (key = value column1, value = value column2)
    dictSeqProb = dict(dfSeqProb.values)
    print(dictSeqProb)
    for i in range(len(outputDf)):
        for AA in aaList:
            numAA = outputDf[AA][i]
            if numAA != 0:
                prob = dictSeqProb.get(AA)
                inter2[AA].append(prob)
            else:
                inter2[AA].append(0)

    sheetName3 = 'InterfaceProbability'
    writeDataframeToSpreadsheet(newDf, newWriter, sheetName3)
    interfaceWriter.save()
    interfaceWriter.close()

    inter2Df = pd.DataFrame.from_dict(inter2)
    total = inter2Df.sum(axis=1)
    newDf = inter2Df.div(total, axis=0)
    dfToSubtract2 = inter2Df.copy()
    newDf.insert(0, 'Interface', outputDf['Interface'])
    inter2Df.insert(0, 'Interface', outputDf['Interface'])
    sheetName1 = 'MembraneSequenceProbability'
    writeDataframeToSpreadsheet(newDf, newWriter, sheetName1)

    print(dfToSubtract1)
    print(dfToSubtract2)

    dfSubtract = dfToSubtract1-dfToSubtract2
    sheetName2 = 'PercentProbabilityDifference'
    dfSubtract.insert(0, 'Interface', outputDf['Interface'])
    total = dfSubtract.sum(axis=1)
    dfSubtract['Percent Difference'] = total
    writeDataframeToSpreadsheet(dfSubtract, newWriter, sheetName2)
    newWriter.save()
    newWriter.close()

def analyzeSequencesWithSameInterface(df, columnsToAnalyze, writer):
    convertInterfaceToX(df)
    removeInterfaceEnds(df)
    interfaceAnalyzer(df, columnsToAnalyze, writer)

# TODO: make this more general so I can add it to utilities
# Analyzes data from a datafram in bins
# what are different ways you could bin by?
# def analyzeBinnedData(df, binName, binRule, numberOfBins, columnNames, outputDir, outFile):
def binAndAverage(df, numberOfBins, binName, columnNames, sheetName, writer):
    i=0
    dictAvg = {}
    dictAvg['Number of Sequences'] = []
    dictAvg['Number of Geometries'] = []
    bins = ['x < -30','-30<x<-25','-25<x<-20','-20<x<-15','-15<x<-10','-10<x<-5']
    addColumnsToDictionary(dictAvg, columnNames)
    while i < numberOfBins:
        if i == 0:
            tmpDf = df[df[binName] < -30]
            getColumnAverages(tmpDf, columnNames, dictAvg)
            numSequences = len(tmpDf)
            dictAvg['Number of Sequences'].append(numSequences)
            dictAvg['Number of Geometries'].append(tmpDf['crossingAngle'].nunique())
            if (numSequences != 0):
                outputProbabilityDataframe(tmpDf, bins[i], writer)
        else:
            # define upper and lower energy bins
            upperBinLim = -30+((i+1)*5)
            lowerBinLim = -30+(i*5)
            # get the dataframe for data within the energy bin limit
            tmpDf = df[df[binName] > lowerBinLim]
            tmpDf = tmpDf[tmpDf[binName] < upperBinLim]
            # get the means for a select number of columns
            getColumnAverages(tmpDf, columnNames, dictAvg)
            numSequences = len(tmpDf)
            dictAvg['Number of Sequences'].append(numSequences)
            dictAvg['Number of Geometries'].append(tmpDf['crossingAngle'].nunique())
            if (numSequences != 0):
                outputProbabilityDataframe(tmpDf, bins[i], writer)
        i+=1

    outputDf = pd.DataFrame.from_dict(dictAvg)
    #print(outputDf)
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
    binAndAverage(dfLeft, numberOfBins, binName, columnNames, sheetNames[1], writer)
    binAndAverage(dfRight, numberOfBins, binName, columnNames, sheetNames[2], writer)

def getInterfaceCount(df):
    count = []
    for i, j in df.iterrows():
        interfaceCount = 0
        for AA in j["InterfaceSeq"][4:18]:
            if AA != "-":
                interfaceCount+=1
        count.append(interfaceCount)
    df["InterfaceCount"] = count

def getInterfaceLeu(df):
    count = []
    for i, j in df.iterrows():
        interfaceCount = 0
        for AA in j["InterfaceSeq"][4:18]:
            if AA == "L":
                interfaceCount+=1
        count.append(interfaceCount)
    df["InterfaceLeu"] = count

def ridOfSequencesWithLessThanXInterfacials(df, numInterface):
    outputDf = pd.DataFrame()
    getInterfaceCount(df)
    getInterfaceLeu(df)
    outputDf = df[df["InterfaceCount"]-df["InterfaceLeu"] > numInterface]
    #outputDf = df
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

#    for i in range(len(aaList)):
#        AA = aaList[i]
#        numAA = j[AA]
#        outputDictSeqProb[AA]
