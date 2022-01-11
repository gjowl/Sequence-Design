#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  9 09:04:42 2020

@author: gloiseau
"""

########################################################################
#                            FUNCTIONS
########################################################################
def counter(row, string1, string2, number1, number2, total):
    count = total
    if row[string1] == number1:
        if row[string2] == number2:
            count += 1
    return count

def binning(numberBins, binTotal):
    binSize = binTotal/numberBins
    D = {}
    bins = 0
    while bins < numberBins:
        D[bins] = 0
        bins += 1
    return D
  
from numpy import zeros
#def makeArrayForBins(bins):
#    C = zeros((bins,bins,bins,bins,bins,bins))
#    return C

def makeArrayForBins(numDist, numAngle, numz1, numz2, numrot1, numrot2):
    arr = zeros((numDist, numAngle, numz1, numz2, numrot1, numrot2))
    return arr
    
#I think the above is a little off: need to actually have 1-5 within each of the bins?
#Convert float to int and then add to the array
def binAdder(row, arr, s1, s2, s3, s4, s5, s6):
    b1 = int(row[s1])
    b2 = int(row[s2])
    b3 = int(row[s3])
    b4 = int(row[s4])
    b5 = int(row[s5])
    b6 = int(row[s6])
    arr[b1][b2][b3][b4][b5][b6] += 1
    return arr

#next is a function to print each combo and each count together
from numpy import vstack
def binPrinter(arr, numDist, numAngle, numz1, numz2, numrot1, numrot2):
    p1 = 0
    arr1 = np.array([])
    indices = np.array([])
    while p1 < numDist:
        p2 = 0
        while p2 < numAngle:
            p3 = 0
            while p3 < numz1:
                p4 = 0
                while p4 < numz2:
                    p5 = 0
                    while p5 < numrot1:
                        p6 = 0
                        while p6 < numrot2:
                            #if arr[p1][p2][p3][p4][p5][p6] != 0:
                            string = ''
                            arr1 = np.append(arr1, arr[p1][p2][p3][p4][p5][p6])
                            string = string + str(p1)
                            string = string + str(p2)
                            string = string + str(p3)
                            string = string + str(p4)
                            string = string + str(p5)
                            string = string + str(p6)
                            indices = np.append(indices, string)
                            p6 += 1
                        p5 +=1
                    p4 += 1
                p3 += 1
            p2 += 1
        p1 += 1  
    a3 = vstack((arr1, indices))
    return a3       

#make it so that it outputs and array and then just choose the number in the array corresponding to the index number

def individualBinCalculator(numberBins, normfactor, binTotal, string):
    arr = np.array([])
    if "Angle" in string:
        binSize = binTotal/numberBins
        previousBin = -1
        currentBin = previousBin + binSize
        binNum = 0
        while binNum < numberBins:
            pBin = previousBin*normfactor
            cBin = currentBin*normfactor
            binString = str(round(pBin,4)) + "-" + str(round(cBin,4))
            arr = np.append(arr, binString)
            previousBin = currentBin
            currentBin = currentBin + binSize
            binNum += 1
    else:
        binSize = binTotal/numberBins
        previousBin = 0
        currentBin = binSize
        binNum = 0
        while binNum < numberBins:
            if "Z" in string:
                pBin = previousBin*normfactor
                cBin = currentBin*normfactor
                binString = str(round(pBin,4)) + "-" + str(round(cBin,4))
                arr = np.append(arr, binString)
                previousBin = currentBin
                currentBin = currentBin + binSize
                binNum += 1
            else:
                pBin = previousBin*normfactor
                cBin = currentBin*normfactor
                binString = str(round(pBin,4)) + "-" + str(round(cBin,4))
                arr = np.append(arr, binString)
                previousBin = currentBin
                currentBin = currentBin + binSize
                binNum += 1
    return arr             

def individualBinCalculatorDist(numberBins, normfactor, addDist, binTotal, string):
    arr = np.array([])
    binSize = binTotal/numberBins
    previousBin = 0
    currentBin = binSize
    binNum = 0
    while binNum < numberBins:
        pBin = previousBin*normfactor + addDist
        cBin = currentBin*normfactor + addDist
        binString = str(round(pBin,4)) + "-" + str(round(cBin,4))
        arr = np.append(arr, binString)
        previousBin = currentBin
        currentBin = currentBin + binSize
        binNum += 1
    return arr 

def binPerIndex(df,  dist, angle, z1, z2, rot1, rot2, row):
    dfnew = pd.DataFrame()
    dfnew = df
    dfnew["dist"].append(dist[row["Index"][0]])
    dfnew["angle"].append(angle[row["Index"][1]])
    dfnew["z1"].append(z1[row["Index"][2]])
    dfnew["z2"].append(z2[row["Index"][3]])
    dfnew["rot1"].append(rot1[row["Index"][4]])
    dfnew["rot2"].append(rot2[row["Index"][5]])
    return dfnew

########################################################################
#                            READ FILE
########################################################################
import pandas as pd
import numpy as np
import datetime
now = datetime.datetime.now()
year = '{:02d}'.format(now.year)
month = '{:02d}'.format(now.month)
day = '{:02d}'.format(now.day)
hour = '{:02d}'.format(now.hour)
minute = '{:02d}'.format(now.minute)
date = '{}_{}_{}'.format(year, month, day)

print('Date: ' + date)

data = pd.DataFrame()
def checkDataset():
    parallel = input('Do you want to analyze only parallel data: T or F?')
    if parallel == "T" or parallel == "t":
        return True
    else:
        return False
    
parallel = checkDataset()

print(parallel)

data = data.append(pd.read_csv('/exports/home/gloiseau/Documents/interhelicalCoordAnalysis/binInterhelicalCoordinatesTemp.csv', delimiter = '\t'))

########################################################################
#               DEFINE BINS AND VARIABLES FOR BINNING
########################################################################
numDistBins = 4
numAngleBins = 8
numz1Bins = 6
numz2Bins = 6
numrot1Bins = 5
numrot2Bins = 5

binTotal = 1
binTotalAngle = 2

#string variables
axDist = "Axial distance"
angle = "Angle"
z1 = "Z' 1"
z2 = "Z' 2"
rot1 = "ω' 1"
rot2 = "ω' 2"

#bin string variables
bAng = "BinAngle"
bDist = "BinDist"
bZ1 = "BinZ1"
bZ2 = "BinZ2"
bRot1 = "Binω1"
bRot2 = "Binω2"

#normalization factors
normDist = 6.6
addDist = 6.2 # use whatever was substrcted from the interhelicalCoordinatesAnalyzer
normAngle = 180
if parallel is True:
    normAngle = 50
normz = 6
normrot = 100

binAngle = np.array([])
binDist = np.array([])
binZ1 = np.array([])
binZ2 = np.array([])
binrot1 = np.array([])
binrot2 = np.array([])
binArray = np.array([])
########################################################################
#                    BIN THE DATA INDIVIDUALLY
########################################################################

count = 0
#for index, row in data.iterrows():
    #if count < 100:
        #binsDist = addToBin(row, numberOfBins, binTotal, binsDist, "Axial distance")
    #binDist = np.append(binDist, addToBinArray(row, numberOfBins, binTotal, axDist))
    #binAngle = np.append(binAngle, addToBinArray(row, numberOfBins, binTotalAngle, angle))
    #binZ1 = np.append(binZ1, addToBinArray(row, numberOfBins, binTotal, z1))
    #binZ2 = np.append(binZ2, addToBinArray(row, numberOfBins, binTotal, z2))
    #binrot1 = np.append(binrot1, addToBinArray(row, numberOfBins, binTotal, rot1))
    #binrot2 = np.append(binrot2, addToBinArray(row, numberOfBins, binTotal, rot2))
    #count += 1

#what I need to get is a way to only add the part of the array that matches with certain parts of the array in one category
count = 0
binCount = 0
arrBin = makeArrayForBins(numDistBins, numAngleBins, numz1Bins, numz2Bins, numrot1Bins, numrot2Bins)
print(arrBin[0][0][0][0][0][0])
for index, row in data.iterrows():
    #if count < 100:
    #arrBin = binAdder(row, arrBin, bAng, bDist, bZ1, bZ2, bRot1, bRot2)
    arrBin = binAdder(row, arrBin, bDist, bAng, bZ1, bZ2, bRot1, bRot2) 
    #Above: flipped Angle and distance to see if I could see distance trends
    #count += 1
print(arrBin[3][1][1][1][1][1])
newArr = binPrinter(arrBin, numDistBins, numAngleBins, numz1Bins, numz2Bins, numrot1Bins, numrot2Bins)

df = pd.DataFrame()
df["Count"] = newArr[0]
df["Index"] = newArr[1]

#after making this dataframe, can I then read the dataframe index in such a way to write out the actual start-end slice?

binDist = individualBinCalculatorDist(numDistBins, normDist, addDist, binTotal, axDist)
binAngle = individualBinCalculator(numAngleBins, normAngle, binTotalAngle, angle)
binZ1 = individualBinCalculator(numz1Bins, normz, binTotal, z1)
binZ2 = individualBinCalculator(numz2Bins, normz, binTotal, z2)
binrot1 = individualBinCalculator(numrot1Bins, normrot, binTotal, rot1)
binrot2 = individualBinCalculator(numrot2Bins, normrot, binTotal, rot2)

print(binDist)
print(binAngle)
print(binZ1)
print(binrot1)

#for bin start-end
dists = np.array([])
angs = np.array([])
z1s = np.array([])
z2s = np.array([])
rot1s = np.array([])
rot2s = np.array([])

for index, row in df.iterrows():
    dists = np.append(dists, binDist[int(row["Index"][0])])
    angs = np.append(angs, binAngle[int(row["Index"][1])])
    z1s = np.append(z1s, binZ1[int(row["Index"][2])])
    z2s = np.append(z2s, binZ2[int(row["Index"][3])])
    rot1s = np.append(rot1s, binrot1[int(row["Index"][4])])
    rot2s = np.append(rot2s, binrot2[int(row["Index"][5])])
    #df1 = df1.append(binPerIndex(df1, binDist, binAngle, binZ1, binZ2, binrot1, binrot2, row))
df["dist"] = dists
df["angle"] = angs
df["z1"] = z1s
df["z2s"] = z2s
df["rot1"] = rot1s
df["rot2"] = rot2s

#########################################################################
##                    CONVERT DATA TO CSV
#########################################################################
if parallel is True:
    df.to_csv('/exports/home/gloiseau/Documents/interhelicalCoordAnalysis/2020_01_20_parallelbincounts.csv', sep='\t')
else:
    df.to_csv('/exports/home/gloiseau/Documents/interhelicalCoordAnalysis/2020_01_20_bincounts.csv', sep='\t')
