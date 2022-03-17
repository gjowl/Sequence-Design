"""
Created on Mon Sep 13 18:37:30 2021

@author: gjowl
"""
"""
This piece of code is for writing a csv file that can be used to purchase a CHIP, similar to Samantha's CHIP4.
  - Read in the CHIP primer file to choose primers for segments (24 pairs of primers, so up to 24 segments can be made)
  - Extract a list of amino acid sequences from a DataFrame and convert it to nucleic acid sequences with proper cutsites and primers
  - Write output file for CHIP
"""
from datetime import date
from scipy import stats
from matplotlib import gridspec
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import re
import random as rand
from utility import *
import dnachisel
from dnachisel.biotools import reverse_translate

#Functions
def getPrimerSet(dfFwd, dfRvs, row):
    fwdPrimer = dfFwd['Fwd'][row-1]
    revPrimer = dfRvs['Rvs'][row-1]
    return fwdPrimer, revPrimer

def getRandomDNAEnd(length):
    randSeq = ""
    DNA = ['g', 'a', 't', 'c']
    while len(randSeq) < length:
        randSeq = randSeq+rand.choice(DNA)
    return randSeq
# Variables
currDir_path = os.path.dirname(os.path.realpath(__file__))
outputDir = currDir_path + '/Analysis'
inputFile = outputDir + '/optimizedBackboneAnalysis.xlsx'
primerFile = outputDir+"/Primers.csv"
outputFile = outputDir + '/CHIP.xlsx'
writer = pd.ExcelWriter(outputFile)
cutSite1 = 'gctagc'
cutSite2 = 'gatc'
gpa = ''
g83i = ''
pccKan = ''
randomDNALength = 21 #matches the number from Samantha's CHIP4

# Read in CHIP primer file
dfPrimer = pd.read_csv(primerFile, sep=',')

# Separate Primers and primer names
#go through list of primers
dfForwardPrimer = dfPrimer.iloc[0::2]
dfReversePrimer = dfPrimer.iloc[1::2]
dfForwardPrimer = dfForwardPrimer.reset_index()
dfReversePrimer = dfReversePrimer.reset_index()
dfForwardPrimer.pop('index')
dfReversePrimer.pop('index')

# Main
dfAllSequences = pd.read_excel(inputFile, sheet_name='Segments')

totalSegments = dfAllSequences['SegmentNumber'].max()
dictOutput = {}
colNames = ['Segment Number', 'TM Sequence', 'DNA Sequence']
addColumnsToDictionary(dictOutput, colNames)

# Goes through all of the segments and converts each protein sequence to nucleic acid sequence
for segmentNum in dfAllSequences['SegmentNumber'].unique():
    dfSegment = dfAllSequences[dfAllSequences['SegmentNumber'] == segmentNum]
    sequenceList = dfSegment["Sequence"]
    fwd, rvs = getPrimerSet(dfForwardPrimer, dfReversePrimer, segmentNum)
    for sequence in sequenceList
    #TODO: break these into functions
        randomDNAEnd = getRandomDNAEnd(randomDNALength)
        while randomDNAEnd.find(fwd) is True or randomDNAEnd.find(rvs) is True:
            randomDNAEnd = getRandomDNAEnd(randomDNALength)
        DNASeq = reverse_translate(sequence[0:18])
        while DNASeq.find(fwd) is True or DNASeq.find(rvs) is True:
            DNASeq = reverse_translate(sequence[0:18])
        seqForChip = fwd + cutSite1 + DNASeq + cutSite2 + rvs + randomDNAEnd
        dictOutput['DNA Sequence'].append(seqForChip)
        dictOutput['Segment Number'].append(segmentNum)
        dictOutput['TM Sequence'].append(sequence[0:18])
    #TODO: at end of segment, add in the control sequences with a function
    dictOutput['DNA Sequence'].append(seqForChip)
    dictOutput['Segment Number'].append(segmentNum)
    dictOutput['TM Sequence'].append(sequence[0:18])

outputDf = pd.DataFrame.from_dict(dictOutput)
writeDataframeToSpreadsheet(outputDf, writer, 'CHIPtest')

writer.close()
