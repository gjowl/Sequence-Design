#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  4 10:32:10 2020

This script analyzes data from interhelicalCoordinates.cpp runs

TODO:
1. edit so that there's a list of variables that can be changed and used throughout this code

1. find all the pdbs with at least one interacting helical pair
2. go into the pairGeometryReport and search for lines with all 6 coordinates
3. compile these lines into a file? Or should I take the values from those and convert them to normalized values?
   0-1 for z` and omega` (for both helices), 0-1 for distances from 6.5-11, and -1-1 for crossing angle

@author: gloiseau
"""

import os, sys
import pandas as pd
import datetime
from fuzzywuzzy import fuzz
from difflib import SequenceMatcher
import re
import numpy as np

########################################################################
#                             FUNCTIONS
########################################################################

def getListOfDir(dirName):
    # create a list of file and sub directories
    # names in the given directory
    listOfDir = os.listdir(dirName)
    allDir = []
    # Iterate over all the entries
    for entry in listOfDir:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # Check if entry is a directory
        if os.path.isdir(fullPath):
            allDir.append(fullPath)
    return allDir

#checks for only "pair_" files
def checkPairFiles(dirName):
    # create a list of file and sub directories
    # names in the given directory
    listOfDir = os.listdir(dirName)
    # Iterate over all the entries
    for entry in listOfDir:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        if 'pair_' in fullPath:
            return True
    return False

def pairGeometryFile(dirName):
    # create a list of file and sub directories
    # names in the given directory
    listOfDir = os.listdir(dirName)
    pairFile = ''
    # Iterate over all the entries
    for entry in listOfDir:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        if 'pairGeometry' in fullPath:
            pairFile = fullPath
    return pairFile

def usePreviousData():
    answer = input("Use previously extracted data? T or F")
    if answer == "T" or answer == "t":
        return True
    else:
        return False

def analyzeSolubleProteins():
    sp = input("Analyze soluble proteins?")
    if sp == "T" or sp == "t":
        return True
    else:
        return False

def getListOfFiles(dirName):
    # create a list of file and sub directories
    # names in the given directory
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            allFiles.append(fullPath)
    return allFiles

#Below functions for getDuplicates function
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()
    #return fuzz.ratio(a, b)

def checkBoolNum(dstart, dend, start, end):
    if dstart in range(start-5, start+5) and dend in range(end-5, end+5):
        return True
    else:
        return False

def checkBoolStr(c1, c2):
    if c1 == c2:
        return True, False
    else:
        return False, True

def checkSeqSimilarity(dseq1, dseq2, seq1, seq2):
    s1 = similar(dseq1, seq1)
    s2 = similar(dseq2, seq2)
    if s1 > 0.95 and s2 > 0.95:
        return True
    else:
        return False

#Function to define which sequences are duplicates by defining unique 0 and duplicates 1
#TODO: At some point it would probably be better to transition this to a dictionary
def getDuplicates(df):
    dupl = np.array([])
    r1 = np.array([])
    r2 = np.array([])
    r3 = np.array([])
    r4 = np.array([])
    r5 = np.array([])
    copyof = np.array([])
    #reason.columns = ["Segment 1", "Segment 2", "Chain AA", "Chain AB", "Sequence Similarity"]
    for index, row in df.iterrows():
        if df["Num"][index] == 0:
            dupl = np.append(dupl, 0)
            num11 = []
            num12 = []
            num21 = []
            num22 = []
            chainAA = []
            chainAB = []
            seq1 = []
            seq2 = []
            num11.append(df["Seg 1 Pos start #"][index])
            num12.append(df["Seg 1 Pos end #"][index])
            num21.append(df["Seg 2 Pos start #"][index])
            num22.append(df["Seg 2 Pos end #"][index])
            seq1.append(df["Sequence 1"])
            seq2.append(df["Sequence 2"])
            r1 = np.append(r1, True)
            r2 = np.append(r2, True)
            r5 = np.append(r5, True)
            copyof = np.append(copyof, "x")
            if df["Seg 1 Pos start Id"][index][0] == df["Seg 2 Pos start Id"][index][0]:
                chainAA.append(True)
                chainAB.append(False)
                r3 = np.append(r3, True)
                r4 = np.append(r4, False)
            else:
                chainAA.append(False)
                chainAB.append(True)
                r3 = np.append(r3, False)
                r4 = np.append(r4, True)
        else:
            tnum11 = df["Seg 1 Pos start #"][index]
            tnum12 = df["Seg 1 Pos end #"][index]
            tnum21 = df["Seg 2 Pos start #"][index]
            tnum22 = df["Seg 2 Pos end #"][index]
            tseq1 = df["Sequence 1"][index]
            tseq2 = df["Sequence 2"][index]
            cAA, cAB = checkBoolStr(df["Seg 1 Pos start Id"][index][0], df["Seg 2 Pos start Id"][index][0])
            for i in range(0,len(num11)):
                seg1 = checkBoolNum(tnum11, tnum12, num11[i], num12[i])
                seg2 = checkBoolNum(tnum21, tnum22, num21[i], num22[i])
                sim = checkSeqSimilarity(tseq1, tseq2, seq1[i], seq2[i])
                if seg1 == True and seg2 == True and chainAA[i] == cAA and chainAB[i] == cAB and sim == True:
                    dupl = np.append(dupl, 1)
                    copyof = np.append(copyof, i)
                    r1 = np.append(r1, seg1)
                    r2 = np.append(r2, seg2)
                    r3 = np.append(r3, chainAA[i])
                    r4 = np.append(r4, chainAB[i])
                    r5 = np.append(r5, sim)
                    break
                elif i == len(num11)-1:
                    dupl = np.append(dupl, 0)
                    copyof = np.append(copyof, "x")
                    r1 = np.append(r1, seg1)
                    r2 = np.append(r2, seg2)
                    r3 = np.append(r3, chainAA[i])
                    r4 = np.append(r4, chainAB[i])
                    r5 = np.append(r5, sim)
                    num11.append(tnum11)
                    num12.append(tnum12)
                    num21.append(tnum21)
                    num22.append(tnum22)
                    chainAA.append(cAA)
                    chainAB.append(cAB)
                    seq1.append(tseq1)
                    seq2.append(tseq2)
                    break
                else:
                    continue
    return dupl, r1, r2, r3, r4, r5, copyof

########################################################################
#             FIND PDBS WITH AT LEAST ONE INTERACTING PAIR
########################################################################
now = datetime.datetime.now()
year = '{:02d}'.format(now.year)
month = '{:02d}'.format(now.month)
day = '{:02d}'.format(now.day)
hour = '{:02d}'.format(now.hour)
minute = '{:02d}'.format(now.minute)

currDir = os.getcwd()
dataDir = sys.argv[1]
#doesn't get them in order, but I don't think that should matter
alldata = pd.DataFrame()
proteinDir = 'membraneProteins'
outputDir = currDir + '/' + proteinDir
os.makedirs(outputDir, exist_ok=True)

########################################################################
#                  CHECK WHICH DATABASE TO ANALYZE
########################################################################
print("Analyzing membrane protein database...")
dirName = dataDir

########################################################################
#         READ PAIR CSV FILES INTO DATAFRAME AND OUTPUT AS CSV
########################################################################
listOfDir = getListOfDir(dirName)
allPairs = []
count = 0

for elem in listOfDir:
    if checkPairFiles(elem):
        allPairs.append(pairGeometryFile(elem))
        count += 1

for pair in allPairs:
    df = pd.read_csv(pair, delimiter='\t')
    # append data using concat
    alldata = pd.concat([alldata, df], sort=False)
# make a copy of the index column called "Num"
alldata["Num"] = alldata.index
alldata = alldata.reset_index(drop=True)
alldata.describe()
alldata.head()
alldata.to_csv(outputDir +'/allData.csv', sep=',')
print("CSV files read! Output as CSV: ", outputDir + '/allData.csv')

########################################################################
#                  SEPARATE OUT UNNECESSARY DATA
########################################################################
splitdata = pd.DataFrame()
splitdata = alldata

dupl, r1, r2, r3, r4, r5, copyof = getDuplicates(splitdata)
splitdata["Duplicates"] = dupl
splitdata["Segment 1"] = r1
splitdata["Segment 2"] = r2
splitdata["Chain AA"] = r3
splitdata["Chain AB"] = r4
splitdata["Sequence Similarity"] = r5
splitdata["Copy of..."] = copyof

splitdata.to_csv(outputDir +'/allData_all.csv', sep=',')
splitdata = splitdata[splitdata["Duplicates"] == 0]
splitdata = splitdata[splitdata["Z 1"].notnull()]
splitdata = splitdata[splitdata["ω 1"].notnull()]
splitdata = splitdata[splitdata["Z 2"].notnull()]
splitdata = splitdata[splitdata["ω 2"].notnull()]
df = pd.DataFrame()

#only uses the columns that I need
cols = []
cols = [0, 1, 3, 4, 8, 10, 11, 17, 18, 19, 23, 24, 30, 31, 34, 35, 36, 37, 38, 39, 40, 41] #This works when extracting all data, but not when using a saved data file
#If the code breaks because you forgot to fix things, the variables still hold it, so just comment the below out and use that
df = splitdata[splitdata.columns[cols]].copy(deep=True)
print("Separation of unncessary data finished!")

########################################################################
#                PATTERN MATCHING FOR HELICAL MASKS
########################################################################
acceptRatio = 70
bestPattern = "HHHHPPHHPPHHHH"

dfhm = pd.DataFrame()

# This checks the ratio between the pattern and the matched portion of the string
ratios1 = []
ratios2 = []
for hm in df["Helical mask 1"]:
    if re.search(bestPattern, hm, re.IGNORECASE):
        hm1 = re.search(bestPattern, hm, re.IGNORECASE)
        if fuzz.ratio(hm1.group(0), bestPattern) > acceptRatio:
            ratios1.append(1)
        else:
            ratios1.append(None)
    else:
        ratios1.append(None)

for hm in df["Helical mask 2"]:
    if re.search(bestPattern, hm, re.IGNORECASE):
        hm1 = re.search(bestPattern, hm, re.IGNORECASE)
        if fuzz.ratio(hm1.group(0), bestPattern) > acceptRatio:
            ratios2.append(1)
        else:
            ratios2.append(None)
    else:
        ratios2.append(None)

# I get a warning for these but I think it still works properly? TODO: fix this warning
df['HM1_ratio'] = ratios1
df['HM2_ratio'] = ratios2

df = df[df['HM1_ratio'].notnull() | df['HM2_ratio'].notnull()]
print("Pattern matching finished!")

########################################################################
#                WRITE OUTPUT FILES BEFORE NORMALIZATION
########################################################################
anti = pd.DataFrame()
anti = df.copy(deep=True)
anti = anti[anti["Angle"] < -90]
anti = anti.append(df[df["Angle"] > 90], sort=False)
anti = anti[anti["Axial distance"] >= 6.2]

anti.to_csv(outputDir +'/antiparallel.csv', sep=',')

parallel = pd.DataFrame()
parallel = df.copy(deep=True)
parallel = parallel[parallel["Angle"] >= -90]
parallel = parallel[parallel["Angle"] <= 90]
parallel = parallel[parallel["Axial distance"] >= 6.2]

parallel.to_csv(outputDir +'/parallel.csv', sep=',')

########################################################################
#                   NORMALIZE EACH DATA COLUMN
########################################################################
excludeRMSD = pd.DataFrame()
excludeRMSD = df.copy(deep=True)
excludeRMSD = excludeRMSD[excludeRMSD["Fit RMSD 1"] < 0.5]
excludeRMSD = excludeRMSD[excludeRMSD["Fit RMSD 2"] < 0.5]

#exclude should probably happen a little earlier
#normalize all
normdf = pd.DataFrame()
normdf = excludeRMSD.copy(deep=True)

normdf["Z' 1"] = normdf["Z' 1"].div(6)
normdf["Z' 2"] = normdf["Z' 2"].div(6)
normdf["ω' 1"] = normdf["ω' 1"].div(100)
normdf["ω' 2"] = normdf["ω' 2"].div(100)
normdf["Angle"] = normdf["Angle"].div(180)
normdf["Axial distance"] = normdf["Axial distance"].sub(6.2).div(6.6)
normdf = normdf[normdf["Axial distance"] > 0]

#normalize parallel region
normpar = pd.DataFrame()
normpar = parallel.copy(deep=True)
normpar = normpar[normpar["Fit RMSD 1"] < 0.5]
normpar = normpar[normpar["Fit RMSD 2"] < 0.5]

normpar.to_csv(outputDir + '/parallel_unnorm.csv', sep=',')

normpar["Z' 1"] = normpar["Z' 1"].div(6)
normpar["Z' 2"] = normpar["Z' 2"].div(6)
normpar["ω' 1"] = normpar["ω' 1"].div(100)
normpar["ω' 2"] = normpar["ω' 2"].div(100)
normpar["Angle"] = normpar["Angle"].div(50)
normpar["Axial distance"] = normpar["Axial distance"].sub(6.2).div(6.6)
normpar = normpar[normpar["Axial distance"] > 0]

#normalize antiparallel region
normanti = pd.DataFrame()
normanti = anti.copy(deep=True)
normanti = normanti[normanti["Fit RMSD 1"] < 0.5]
normanti = normanti[normanti["Fit RMSD 2"] < 0.5]

normanti.to_csv(outputDir + '/antiparallel_unnorm.csv', sep=',')

normanti["Z' 1"] = normanti["Z' 1"].div(6)
normanti["Z' 2"] = normanti["Z' 2"].div(6)
normanti["ω' 1"] = normanti["ω' 1"].div(100)
normanti["ω' 2"] = normanti["ω' 2"].div(100)
normanti["Angle"] = normanti["Angle"].div(50)
normanti["Axial distance"] = normanti["Axial distance"].sub(6.2).div(6.6)
normanti = normanti[normanti["Axial distance"] > 0]

# Rid of the numbers on the side (they don't matter)
print("Normalization of data finished!")

########################################################################
#                     WRITE OUTPUT FILE AS CSV
########################################################################
#The above adds on an extra column right at the beginning
df.to_csv(outputDir + '/splitData.csv', sep='\t')
normdf.to_csv('/exports/home/gloiseau/Documents/interhelicalCoordAnalysis/' + proteinDir + '/alldata_norm.csv', sep='\t')
normpar.to_csv('/exports/home/gloiseau/Documents/interhelicalCoordAnalysis/' + proteinDir + '/parallel_norm.csv', sep='\t')
normanti.to_csv('/exports/home/gloiseau/Documents/interhelicalCoordAnalysis/' + proteinDir + '/antiparallel_norm.csv', sep='\t')

print("finished")
