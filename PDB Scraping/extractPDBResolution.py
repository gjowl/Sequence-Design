#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 12:36:57 2020

This script extracts the PDB resolution from each

@author: gloiseau
"""

#Extract resolution from pdb files

#I already have all of the pdb files, so I should be able to search in those for the resolution?
import os
from biopandas.pdb import PandasPdb as bpd
import pandas as pd
import numpy as np

########################################################################
#                            FUNCTIONS
########################################################################
def digitCounter(number):
    #Number = int(input("Please Enter any Number: "))
    c = -1
    while(number > 0):
        number = number // 10
        c = c + 1
    if c < 10:
        count = '0' + str(c)
        return count
    else:
        count = str(c)
        return count

def findResInPdb(data, pdbid):
    d = data.df["OTHERS"]
    d1 = d[d["entry"].str.contains("2 RESOLUTION.  ")] #the spaces are necessary here for some pdbs and should work for most
    resolution = str(d1["entry"])
    try:
        resolution = float(resolution[25:30])
        return resolution, pdbid
    except:
        d2 = d[d["record_name"].str.contains("EXPDTA")]
        resolution = str(d2["entry"])
        #need to add in a key type here to check what type of data it is and convert to a number
        #binning won't work unless all resolutions are numeric; for now I just deleted them manually
        return 100, pdbid #temporary fix for all non-x-ray structures

def getRes(row, pdb, prevRes, prevID):
    pdbid = row["PDB Id"]
    if pdbid in prevID:
        return prevRes, prevID
    else:
        try:
            path = bpd().fetch_pdb(pdbid)
            #path = pdb + pdbid + ".pdb"
            #data = bpd().read_pdb(path)
            resolution, pdbid = findResInPdb(path, pdbid)
            return resolution, pdbid
        except:
            try:
                x = float(pdbid)
                num = digitCounter(x)
                pdbid = pdbid[0] + "e" + num
                if pdbid in prevID:
                    return prevRes, prevID
                else:
                    path = bpd().fetch_pdb(pdbid)
                    #path = pdb + pdbid + ".pdb"
                    #data = bpd().read_pdb(path)
                    resolution, pdbid = findResInPdb(path, pdbid)
                    return resolution, pdbid
            except:
                print(pdbid)
                #print(path)
                return "x", pdbid
    #print("Resolution: %s" % data.df[""])

def checkDataset():
    parallel = input('Do you want to analyze parallel data: T or F?')
    if parallel == "T" or parallel == "t":
        return True
    else:
        return False

def analyzeSolubleProteins():
    sp = input("Analyze soluble proteins? T or F")
    if sp == "T" or sp == "t":
        return True
    else:
        return False

def compareToDegrado2015():
    cd = input("Have you compared to Degrado 2015? T or F")
    if cd == "T" or cd == "t":
        return True
    else:
        return False

########################################################################
#                            READ FILE
########################################################################
currDir = os.getcwd()
data = pd.DataFrame()
date = input("Insert date in year_month_day format for what data you would like to rerun: ")
sp = analyzeSolubleProteins()

if sp is True:
    proteinDir = "solubleProteins"
else:
    proteinDir = "membraneProteins"

cd = compareToDegrado2015()
if cd is True:
    parallel = checkDataset()
    if parallel is True:
        print("Adding parallel protein database resolutions...")
        data = data.append(pd.read_csv('/exports/home/gloiseau/Documents/interhelicalCoordAnalysis/' + proteinDir +'/' + date + '_parallel_unnorm.csv', delimiter = '\t'))
    elif parallel is False:
        print("Adding antiparallel protein database resolutions...")
        data = data.append(pd.read_csv('/exports/home/gloiseau/Documents/interhelicalCoordAnalysis/' + proteinDir +'/' + date + '_antiparallel_unnorm.csv', delimiter = '\t'))
else:
    data = data.append(pd.read_csv('/exports/home/gloiseau/Documents/interhelicalCoordAnalysis/' + proteinDir +'/' + date + '/membraneProtResolutions.csv', delimiter = '\t'))

########################################################################
#                 EXTRACT PDBIDS AND FIND RESOLUTION
########################################################################
resolutions = np.array([])
pdbPath = '/data02/gloiseau/Sequence_Design_Project/interhelicalCoordinates/' + proteinDir +'/pdbs/'

df = pd.DataFrame()
df = data.copy(deep=True)

count = 0
prevID = ''
res = ''

for index, row in data.iterrows():
    res, prevID = getRes(row, pdbPath, res, prevID)
    resolutions = np.append(resolutions, res)

df["Resolution"] = resolutions

########################################################################
#                     WRITE OUTPUT FILE AS CSV
########################################################################
if cd is True:
    if parallel is True:
        df.to_csv('/exports/home/gloiseau/Documents/interhelicalCoordAnalysis/' + proteinDir +'/' + date + '_parallel_unnorm.csv', sep='\t')
    else:
        df.to_csv('/exports/home/gloiseau/Documents/interhelicalCoordAnalysis/' + proteinDir +'/' + date + '_antiparallel_unnorm.csv', sep='\t')
else:
    df.to_csv('/exports/home/gloiseau/Documents/interhelicalCoordAnalysis/' + proteinDir +'/' + date + '/membraneProtResolutions.csv', sep='\t')
