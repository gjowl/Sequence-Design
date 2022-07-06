# -*- coding: utf-8 -*-
"""
Spyder Editor

"""

"""
This file is used to analyze the pair distribution and spread of the baseline energies from baselineSelfPairComparison_02.cpp
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from matplotlib.backends.backend_pdf import PdfPages

##############################################
#                 FUNCTIONS
##############################################

def appendPairFiles(_date):
    i = int(input("Insert the number of files that need to be checked: "))
    filename = "C:\\Users\\gjowl\\Documents\\" + _date + "_pairEnergyComparison"
    
    df = pd.DataFrame()
    if (i == 1):
        f = filename + ".xlsx"
        df = pd.read_excel(f)
    else:
        f = filename + "1.xlsx"
        df = pd.read_excel(f)
        for num in range(2, i):
            f2 = filename + str(num) + ".xlsx"
            df2 = pd.read_excel(f2)
            df.append(df2)
    return df


def seqPairDist(df):
    prevval = ""
    pdvec = []
    count = 0
    for x in df["pd"]:
        if count == 0:
            prevval = x
        temp = x
        if prevval != temp:
            pdvec.append(count)
            prevval = temp
            count = 0
        if count == len(df):
            pdvec.append(count)
        count = count + 1
    return pdvec

def makeDictForPlots(_df, _pdVec):
    enerArr = []
    blArr = []
    pdDict = {}
    blDict = {}
    currentNum = 0
    for i in _pdVec:
        num = 0
        while num < i:
            enerArr.append(_df["Energy"].iloc[currentNum+num])
            blArr.append(_df["Baseline"].iloc[currentNum+num])
            num = num + 1
        pdDict[_df["pd"].iloc[currentNum]] = enerArr
        blDict[_df["pd"].iloc[currentNum]] = blArr
        enerArr = []
        blArr = []
        currentNum = currentNum + i
    return pdDict, blDict

def plotGraphs(_pdf, _pdDict, _blDict):
    largeVal = 0
    smallVal = 0
    c = 1
    for key, value in _pdDict.items():
        #print(key + ": " + str(len(key)))
        #print(len(value))
        smallVal = min(value)
        largeVal = max(value)
        mn = np.mean(value)
        #print(key + ": " + str((largeVal+smallVal)/2))
        #print(_blDict.get(key)[0])
        fig, ax = plt.subplots(figsize =(10, 7))
        ax.hist(value, bins = np.arange(smallVal, largeVal + 0.01, 0.01))
        #counts, bins, bars = ax.hist(value, bins = 100)
        plt.xlabel("Energy")
        plt.ylabel("Frequency")
        plt.title(key)
        #c = c + 1
        baseline = "Baseline: " + str(_blDict.get(key)[0])
        mn1 = "Mean: " + str(mn)
        #if c == len(value)-1:
        if largeVal != smallVal:
            ax.annotate(baseline,xy=((largeVal+smallVal)/2,50))
            ax.annotate(mn1,xy=((largeVal+smallVal)/2,10))
        else:
            ax.annotate(baseline,xy=((largeVal+smallVal)/2,50))
            ax.annotate(mn1,xy=((largeVal+smallVal)/2,10))
        _pdf.savefig(fig)
        #ax.xaxis.set_major_formatter(mtick.FormatStrFormatter('%.2e'))
        plt.close(fig)
    _pdf.close()
    
##############################################
#          IMPORT FILE INTO PYTHON
##############################################

date = input("Insert date in year_month_day format (ex. 2020_10_09; OR insert NA if you would like default): ")
if date == "NA":
    date = "2020_10_09"

df = appendPairFiles(date)

##############################################
#       GET RID OF ANY ROWS WITH 0
##############################################

df.replace(0, np.nan, inplace=True)
df = df.dropna()

##############################################
#          ADD IN PAIR DISTANCE COLUMN
##############################################

df["pd"] = df["Pair"] + df["Distance"].astype(str)
df = df.sort_values("pd", ascending=True)

##############################################
#       SEPARATE OUTER AND INNER DATA
##############################################

dfIn = df[df["Position1"] > 4]
dfIn = dfIn[dfIn["Position1"] < 27]
dfIn = dfIn[dfIn["Position2"] > 4]
dfIn = dfIn[dfIn["Position2"] < 27]

#dfOut = df[df["Position1"] > 10]
#dfOut = dfOut[dfOut["Position1"] < 16]
dfOut1 = df[df["Position1"] < 5]
dfOut2 = df[df["Position2"] > 26]
dfOut = dfOut1.append(dfOut2)

##############################################
#     DIVIDE DF BY PAIR DISTANCE COLUMN
##############################################

pdVecIn = seqPairDist(dfIn)
pdVecOut = seqPairDist(dfOut)

##############################################
#  EXTRACT ENERGIES FOR PLOT INTO DICTIONARY
##############################################

pdDictIn, blDictIn = makeDictForPlots(dfIn, pdVecIn)
pdDictOut, blDictOut = makeDictForPlots(dfOut, pdVecOut)

# Creating histogram
outArr = []
i = 0
while i < len(pdDictIn):
    outArr.append(5)
    i = i + 1

##############################################
#   PLOT OUT GRAPHS FOR EACH PAIR DISTANCE
##############################################

pdfIn = PdfPages(date + '_pairBaselinePlots.pdf')
pdfOut = PdfPages(date + '_pairBaselinePlotsOuterLeu.pdf')
plotGraphs(pdfIn, pdDictIn, blDictIn)
print(dfIn.shape)
print("Finished 1")
plotGraphs(pdfOut, pdDictOut, blDictOut)
print(dfOut.shape)
print("Finished 2")
