#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  8 09:55:25 2020

@author: gloiseau
"""

#TODO: Write code that bins the data from my runs and then counts them
#1. Need to bin all into a 2d array (6 dimensions, so around 6^5; first start with 0.5 bins)
#2. Make it output a csv
import array as ar

########################################################################
#                            FUNCTIONS
########################################################################
def counter(row, string1, string2, number1, number2):
    count = 0
    if row[string1] == number1:
        if row[string2] == number2:
            count += 1
    return count


def binning(row, numberBins, binTotal, string):
    binSize = binTotal/numberBins
    D = {}
    bins = 0
    if bins < binSize:
        D[bins] = 0
        bins += 1
    print(D)

#TODO: Currently excludes anything where Z and rot are above the threshold: how do I account for these?
def addToBinArray(row, numberBins, binTotal, string):
    if "Angle" in string:
        binSize = binTotal/numberBins
        previousBin = -1
        currentBin = previousBin + binSize
        binNum = 0
        finalBin = 0
        while binNum < numberBins:
            if row[string] <= currentBin and row[string] > previousBin:
                finalBin = binNum
                binNum = numberBins
            else:
                previousBin = currentBin
                currentBin = currentBin + binSize
                binNum += 1
    else:
        binSize = binTotal/numberBins
        previousBin = 0
        currentBin = binSize
        binNum = 0
        finalBin = 0
        while binNum < numberBins:
            if row[string] <= currentBin and row[string] > previousBin:
                finalBin = binNum
                binNum = numberBins
            else:
                previousBin = currentBin
                currentBin = currentBin + binSize
                binNum += 1
    return finalBin

#TODO: This is the same as the above but retursn the string; find a more efficient way to do this
def calcBins(row, numberBins, normfactor, binTotal, string):
    binString = ''
    if "Angle" in string:
        binSize = binTotal/numberBins
        previousBin = -1
        currentBin = previousBin + binSize
        binNum = 0
        while binNum < numberBins:
            if row[string] <= currentBin and row[string] > previousBin:
                binNum = numberBins
                previousBin = previousBin*normfactor
                currentBin = currentBin*normfactor
                binString = str(round(previousBin,4)) + "-" + str(round(currentBin,4))
            else:
                previousBin = currentBin
                currentBin = currentBin + binSize
                binNum += 1
    else:
        binSize = binTotal/numberBins
        previousBin = 0
        currentBin = binSize
        binNum = 0
        while binNum < numberBins:
            if row[string] <= currentBin and row[string] > previousBin:
                binNum = numberBins
                if "Z" in string:
                    previousBin = previousBin*normfactor
                    currentBin = currentBin*normfactor
                    binString = str(round(previousBin,4)) + "-" + str(round(currentBin,4))
                else:
                    #print(previousBin)
                    previousBin = previousBin*normfactor
                    #print(previousBin)
                    currentBin = currentBin*normfactor
                    binString = str(round(previousBin,4)) + "-" + str(round(currentBin,4))
                    #print(binString)
            else:
                previousBin = currentBin
                currentBin = currentBin + binSize
                binNum += 1
    return binString

def calcBinsDist(row, numberBins, normfactor, addDist, binTotal, string):
    binString = ''
    binSize = binTotal/numberBins
    previousBin = 0
    currentBin = binSize
    binNum = 0
    while binNum < numberBins:
        if row[string] <= currentBin and row[string] > previousBin:
            binNum = numberBins
            previousBin = previousBin*normfactor + addDist#TODO: this works for now but only because the upper limit is 12.8
            currentBin = currentBin*normfactor + addDist
            binString = str(round(previousBin,4)) + "-" + str(round(currentBin,4))
        else:
            previousBin = currentBin
            currentBin = currentBin + binSize
            binNum += 1
    return binString

def checkDataset():
    parallel = input('Do you want to analyze only parallel data: T or F?')
    if parallel == "T" or parallel == "t":
        return True
    else:
        return False

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

#data = data.append(pd.read_csv('/exports/home/gloiseau/Documents/interhelicalCoordAnalysis/2020_01_16_normRMSDsplit.csv', delimiter = '\t'))


parallel = checkDataset()

print(parallel)

if parallel is True:
    data = data.append(pd.read_csv('/exports/home/gloiseau/Documents/interhelicalCoordAnalysis/2020_01_20_parallel.csv', delimiter = '\t'))
else:
    data = data.append(pd.read_csv('/exports/home/gloiseau/Documents/interhelicalCoordAnalysis/2020_01_20_normalized.csv', delimiter = '\t'))

########################################################################
#                INPUT RESOLUTION LIMIT AND EXTRACT DATA
########################################################################
resLimit = 3

data = data[data["Resolution"] < resLimit]

########################################################################
#                     WRITE OUTPUT FILE AS CSV
########################################################################
if parallel is True:
    data.to_csv('/exports/home/gloiseau/Documents/interhelicalCoordAnalysis/2020_01_20_parallellimitResolution.csv', sep='\t')
else:
    data.to_csv('/exports/home/gloiseau/Documents/interhelicalCoordAnalysis/2020_01_20_normlimitResolution.csv', sep='\t')

########################################################################
#       INPUT POINT OF CLOSEST APPROACH LIMIT AND EXTRACT DATA
########################################################################
pocaLimit = 3

data = data[data["PoCA shift 1"] < pocaLimit]
data = data[data["PoCA shift 2"] < pocaLimit]

########################################################################
#                            CREATE BIN ARRAYS
########################################################################
#for bin number
binAngle = np.array([])
binDist = np.array([])
binZ1 = np.array([])
binZ2 = np.array([])
binrot1 = np.array([])
binrot2 = np.array([])
binArray = np.array([])
count = 0

#for bin start-end
dists = np.array([])
angs = np.array([])
z1s = np.array([])
z2s = np.array([])
rot1s = np.array([])
rot2s = np.array([])

########################################################################
#                        HOUSEKEEPING VARIABLES
########################################################################
df = pd.DataFrame()
df = data.copy(deep=True)

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

#normalization factors
normDist = 6.6
addDist = 6.2 # use whatever was substrcted from the interhelicalCoordinatesAnalyzer
normAngle = 180
if parallel is True:
    normAngle = 50
normz = 6
normrot = 100

########################################################################
#                          BINNING...
########################################################################
print("Binning...")
for index, row in data.iterrows():
    #if count < 100:
        #binsDist = addToBin(row, numberOfBins, binTotal, binsDist, "Axial distance")
    binDist = np.append(binDist, addToBinArray(row, numDistBins, binTotal, axDist))
    dists = np.append(dists, calcBinsDist(row, numDistBins, normDist, addDist, binTotal, axDist))
    binAngle = np.append(binAngle, addToBinArray(row, numAngleBins, binTotalAngle, angle))
    angs = np.append(angs, calcBins(row, numAngleBins, normAngle, binTotalAngle, angle))
    binZ1 = np.append(binZ1, addToBinArray(row, numz1Bins, binTotal, z1))
    z1s = np.append(z1s, calcBins(row, numz1Bins, normz, binTotal, z1))
    binZ2 = np.append(binZ2, addToBinArray(row, numz2Bins, binTotal, z2))
    z2s = np.append(z2s, calcBins(row, numz2Bins, normz, binTotal, z2))
    binrot1 = np.append(binrot1, addToBinArray(row, numrot1Bins, binTotal, rot1))
    rot1s = np.append(rot1s, calcBins(row, numrot1Bins, normrot, binTotal, rot1))
    binrot2 = np.append(binrot2, addToBinArray(row, numrot2Bins, binTotal, rot2))
    rot2s = np.append(rot2s, calcBins(row, numrot2Bins, normrot, binTotal, rot2))
    #cout += 1
print("Complete!")

########################################################################
#                       PRINT BINS TO DATAFRAME
########################################################################
df['BinDist'] = binDist
df['BinAngle'] = binAngle
df['BinZ1'] = binZ1
df['BinZ2'] = binZ2
df['Binω1'] = binrot1
df['Binω2'] = binrot2
df['dist'] = dists
df['ang'] = angs
df['z1'] = z1s
df['z2'] = z2s
df['rot1'] = rot1s
df['rot2'] = rot2s

########################################################################
#                     WRITE OUTPUT FILE AS CSV
########################################################################
df.to_csv('/exports/home/gloiseau/Documents/interhelicalCoordAnalysis/binInterhelicalCoordinatesTemp.csv', sep='\t')
