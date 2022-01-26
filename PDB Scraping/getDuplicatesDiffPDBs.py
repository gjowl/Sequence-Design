#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  3 13:46:44 2020

@author: gloiseau
"""
import os
import pandas as pd
import datetime
from fuzzywuzzy import fuzz
from difflib import SequenceMatcher
import re
import numpy as np
import csv

#Housekeeping Variables
Z1 = "Z' 1"
Z2 = "Z' 2"
ax1 = "ω' 1"
ax2 = "ω' 2"
ang = "Angle"
dist = "Axial distance"

def check(c1, c2, val):
    if c1 <= val <= c2:
        return True
    return False

#Below functions for getDuplicates function
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()
    #return fuzz.ratio(a, b)

def checkBoolNum(dstart, dend, start, end):
    if dstart in range(start-5, start+5) and dend in range(end-5, end+5):
        return True
    else:
        return False

def checkBoolZ(dz1, dz2, z1, z2):
    dz1 = round(dz1,1)
    dz2 = round(dz2,1)
    z1 = round(z1,1)
    z2 = round(z2,1)
    if dz1 in np.round(np.linspace(z1-0.6, z1+0.6, 13), 1) and dz2 in np.round(np.linspace(z2-0.6, z2+0.6, 13), 1):
        return True
    else:
        return False

def checkBoolAx(dax1, dax2, ax1, ax2):
    dax1 = int(dax1)
    dax2 = int(dax2)
    ax1 = int(ax1)
    ax2 = int(ax2)
    if dax1 in range(ax1-10, ax1+10) and dax2 in range(ax2-10, ax2+10):
    #if ax1-5 <= dax1 <= ax1+5 and ax2-5 <= dax2 <= ax2+5:
    #if check(ax1-5, ax1+5, dax1) == True:
        return True
    else:
        return False

def checkBoolAng(da, a):
    da = int(da)
    #print(a)
    a = int(a)
    if da in range(a-9, a+9):
        return True
    else:
        return False

def checkBoolDist(dd, d):
    dd = round(dd, 1)
    d = round(d, 1)
    #print(np.round(np.linspace(d-0.3, d+0.3, 7), 1))
    if dd in np.round(np.linspace(d-0.3, d+0.3, 7), 1):
    #if d-0.2 <= dd <= d+0.2:
    #if check(d-0.2, d+0.2, dd) == True:
        return True
    else:
        return False

def checkBoolStr(c1, c2):
    if c1 == c2:
        return True
    else:
        return False

def checkSeqSimilarity(dseq1, seq1):
    s1 = similar(dseq1, seq1)
    #s2 = similar(dseq2, seq2)
    #print(s1)
    if s1 > 0.60:
        return True
    else:
        return False

def checkSeqSimilarity1(dseq1, dseq2, seq1, seq2):
    s1 = similar(dseq1, seq1)
    s2 = similar(dseq2, seq2)
    if s1 > 0.80 and s2 > 0.80:
        return True
    else:
        return False

#Function to define which sequences are duplicates by defining unique 0 and duplicates 1
#TODO: At some point it would probably be better to transition this to a dictionary
def getDuplicatesDiffPDB(df):
    dupl = np.array([])
    num = np.array([])
    copyof = np.array([])
    #reason.columns = ["Segment 1", "Segment 2", "Chain AA", "Chain AB", "Sequence Similarity"]
    for index, row in df.iterrows():
        print(index)
        if index == 0:
            count = 0
            dupl = np.append(dupl, 0)
            num = np.append(num, count)
            Z1s = []
            Z2s = []
            ax1s = []
            ax2s = []
            angs = []
            dists = []
            seq2 = []
            pdbs = []
            Z1s.append(df[Z1][index])
            Z2s.append(df[Z2][index])
            ax1s.append(df[ax1][index])
            ax2s.append(df[ax2][index])
            angs.append(df[ang][index])
            dists.append(df[dist][index])
            seq2.append(df["Sequence 2"][index])
            pdbs.append(df["PDB Id"][index])
            copyof = np.append(copyof, "x")
        elif checkSeqSimilarity(df["Sequence 1"][index], df["Sequence 1"][index-1]) == False:
            count = 0
            dupl = np.append(dupl, 0)
            num = np.append(num, count)
            Z1s = []
            Z2s = []
            ax1s = []
            ax2s = []
            angs = []
            dists = []
            seq2 = []
            pdbs = []
            Z1s.append(df[Z1][index])
            Z2s.append(df[Z2][index])
            ax1s.append(df[ax1][index])
            ax2s.append(df[ax2][index])
            angs.append(df[ang][index])
            dists.append(df[dist][index])
            seq2.append(df["Sequence 2"][index])
            pdbs.append(df["PDB Id"][index])
            copyof = np.append(copyof, "x")
        elif checkSeqSimilarity(df["Sequence 1"][index], df["Sequence 1"][index-1]) == True:
            count = count + 1
            tz1 = df[Z1][index]
            tz2 = df[Z2][index]
            tax1 = df[ax1][index]
            tax2 = df[ax2][index]
            tang = df[ang][index]
            tdist = df[dist][index]
            tseq2 = df["Sequence 2"][index]
            tpdb = df["PDB Id"][index]
            for i in range(0, len(Z1s)):
                #if checkSeqSimilarity(tseq2, seq2[i]) == False:
                    #dupl = np.append(dupl, 0)
                    #num = np.append(num, count)
                    #copyof = np.append(copyof, "x")
                    #Z1s.append(tz1)
                    #Z2s.append(tz2)
                    #ax1s.append(tax1)
                    #ax2s.append(tax2)
                    #angs.append(tang)
                    #dists.append(tdist)
                    #seq2.append(tseq2)
                    #pdbs.append(tpdb)
                    #if tpdb == "5zji":
                        #print(i)
                        #print(df["Sequence 1"][index])
                        #print(tseq2)
                        #print(tz1)
                        #print(tax1)
                        #print(tdist)
                        #print(tang)
                    #continue
                #else:
                    Z = checkBoolZ(tz1, tz2, Z1s[i], Z2s[i])
                    ax = checkBoolAx(tax1, tax2, ax1s[i], ax2s[i])
                    d = checkBoolDist(tdist, dists[i])
                    angle = checkBoolAng(tang, angs[i])
                    pdb = checkBoolStr(tpdb, pdbs[i])
                    sim = checkSeqSimilarity(tseq2, seq2[i])
                    if tpdb == "5zji":
                        print(df["Sequence 1"][index])
                        print(tseq2)
                        print(Z)
                        print(ax)
                        print(d)
                        print(angle)
                    if Z == True and ax == True and d == True and angle == True and sim == True and pdb == False:
                        dupl = np.append(dupl, 1)
                        num = np.append(num, count)
                        copyof = np.append(copyof, i)
                        #Z1s.append(tz1)
                        #Z2s.append(tz2)
                        #ax1s.append(tax1)
                        #ax2s.append(tax2)
                        #angs.append(tang)
                        #dists.append(tdist)
                        #seq2.append(tseq2)
                        break
                    elif i == len(Z1s)-1:
                        dupl = np.append(dupl, 0)
                        num = np.append(num, count)
                        copyof = np.append(copyof, "x")
                        Z1s.append(tz1)
                        Z2s.append(tz2)
                        ax1s.append(tax1)
                        ax2s.append(tax2)
                        angs.append(tang)
                        dists.append(tdist)
                        seq2.append(tseq2)
                        pdbs.append(tpdb)
                        break
                    else:
                        continue
    return dupl, num, copyof

alldata = pd.read_csv('/exports/home/gloiseau/Documents/interhelicalCoordAnalysis/membraneProteins/2020_02_21/splitData_sorted.csv', delimiter=',')

df = alldata
dupl, num, copy = getDuplicatesDiffPDB(df)

df["Duplicate"] = dupl
df["Number"] = num
df["Copy of..."] = copy

df.to_csv('/exports/home/gloiseau/Documents/interhelicalCoordAnalysis/membraneProteins/2020_02_21/tmp.csv', sep='\t')
