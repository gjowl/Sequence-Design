#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  4 10:32:10 2020

This script filters the data from the interhelical coordinates and only keeps non-redundant proteins from a list of proteins from the pisces database.

@author: gloiseau
"""
import os
import pandas as pd

#Check if PDB Id is in list of pdbs that should be accepted: 2020_03_04
#needed a quick way to get my data without rerunning interhelicalCoordinates on everything after filtering

#Variables
currDir = os.getcwd()
inputFile = '/exports/home/gloiseau/Documents/interhelicalCoordAnalysis/membraneProteins/2020_02_21/splitData.csv'
proteinList = '/exports/home/gloiseau/Downloads/bc-30.out'

########################################################################
#                        READ ALL PDBS FROM PISCES
########################################################################
lines = []
strings = []
extras = []
chains = []

with open(proteinList, 'rt') as inputfile:
    for line in inputfile:
        l = line.split()
        pdb = l[0][:4].lower()
        if pdb not in strings:
            if pdb not in extras:
                strings.append(pdb)
            else:
                for i in range(1, len(l)):
                    pdb2 = l[i][:4].lower()
                    if pdb2 not in strings and pdb2 not in extras:
                        strings.append(pdb)
                        break
                    else:
                        continue
        for i in range(1,len(l)):
            extras.append(l[i][:4].lower())

########################################################################
#            READ FILE AND RID CLASSIFY REDUNDANT SEQUENCES
########################################################################
df = pd.read_csv(inputFile, sep='\t')

redundant = []
for id in df["PDB Id"]:
    if id in strings:
        redundant.append(0)
    else:
        redundant.append(1)

df["Redundant"] = redundant
df.to_csv(currDir + '/splitData_bc30.csv', sep='\t')

#TODO: remove anything redundant and save to a file
