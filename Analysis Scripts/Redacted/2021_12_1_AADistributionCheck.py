# @Author: Gilbert Loiseau
# @Date:   2021-12-02
# @Filename: 2021_12_1_AADistributionCheck.py
# @Last modified by:   Gilbert Loiseau
# @Last modified time: 2021-12-09



#This file will take a csv of sequences and read every other row of them,
#then get the sequence entropy


from datetime import date
from scipy import stats
from matplotlib import gridspec
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import re
import seaborn as sns
from designFunctions import *

today = date.today()
today = today.strftime("%Y_%m_%d")
inputFile = "C:\\Users\\gjowl\\Downloads\\5290seqs.csv"
#inputFile = "C:\\Users\\gjowl\\Documents\\Senes Lab\\Design Research\\Sequence Design\\2021_12_03_SequencesFromMembraneProteinAnalysis.csv"
df = pd.read_csv(inputFile, sep='\t')

def getAACountInterface(seqList, AA, dict):
    AAcount = 0
    for seq in seqList:
        for pos in range(len(seq)):
            if AA == seq[pos]:
                AAcount+=1
    dict[AA].append(AAcount)
#count = []
#for i, j in df.iterrows():
#    interfaceCount = 0
#    for AA in j["InterfaceSeq"][3:18]:
#        if AA != "L":
#            interfaceCount+=1
#    count.append(interfaceCount)
#df.loc[:, "InterfaceCount"] = count




# TODO: add in a list of AAs used that gets autogenerated from the config file and put in here
listAA = ["A", "F", "G", "I", "L", "S", "T", "V", "W", "Y"]

def getAADistribution(df, listAA):
    outputDir = "C:\\Users\\gjowl\\Documents\\"
    outFile = outputDir + '2021_12_06_AADistributionCheck_testCheck.xlsx'
    #outFile = outputDir + '2021_12_3_SequencesFromMembraneAnalysisAADistributionCheck.xlsx'
    writer = pd.ExcelWriter(outFile)
    dictAA = {}
    addColumnsToDictionary(dictAA, listAA)
    print(df.iloc[:,18])
    df = df[df.iloc[:, 18] > 0]
    seqList = df.iloc[:,21]
    print(df.iloc[:,21])
    #seqList = df["Sequence"]
    for AA in listAA:
        getAACount(seqList, AA, dictAA)
    outputDf = pd.DataFrame.from_dict(dictAA)
    outputDf["Total"] = outputDf.sum(axis=1)
    totalAAs = outputDf.iloc[0]["Total"]
    print(totalAAs)
    print(outputDf)
    newRow = outputDf.div(totalAAs)
    print(newRow)
    outputDf = outputDf.append(newRow, ignore_index=True)
    print(outputDf)
    writeDataframeToSpreadsheet(outputDf, writer, "AATotals")
    writer.save()
    writer.close()
