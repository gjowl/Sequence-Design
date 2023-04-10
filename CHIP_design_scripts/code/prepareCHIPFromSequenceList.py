"""
Created on Mon Sep 13 18:37:30 2021

@author: gjowl
"""
"""
This piece of code is for writing a csv file that can be used to purchase a CHIP, similar to Samantha's CHIP4.
  - Reads in the CHIP primer file to choose primers for segments (24 pairs of primers, so up to 24 segments can be made)
  - Extract a list of amino acid sequences from a DataFrame made by optimizedBackboneAnalysis and converts it to
    nucleic acid sequences with proper cutsites and primers
  - Writes the output file for CHIP to be submitted to a vendor (TwistBiosciences or Agilent)

TODO:
    - Write in a way to output the proper energies for each sequence
"""
import os, sys, pandas as pd
from datetime import date
from scipy import stats
from matplotlib import gridspec
import os
import matplotlib.pyplot as plt
import numpy as np
import re
import random as rand
import dnachisel
from dnachisel.biotools import reverse_translate

#Functions
# Add column names to dictionary
def addColumnsToDictionary(dict, colNames):
        for i in colNames:
            dict[i] = []

def writeDataframeToSpreadsheet(df, writer, sheetName):
    df.to_excel(writer, sheet_name=sheetName)

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

def getCHIPFile(df, dfFwdP, dfRevP, gpaSeq, g83ISeq, cut1, cut2, randomDNALength):
    dictOutput = {}
    colNames = ['Segment Number', 'TM Sequence', 'DNA Sequence']
    addColumnsToDictionary(dictOutput, colNames)
    for segmentNum in df['Segment'].unique():
        dfSegment = df[df['Segment'] == segmentNum]
        sequenceList = dfSegment["Sequence"]
        fwd, rvs = getPrimerSet(dfFwdP, dfRevP, segmentNum)
        # For every sequence, make a random string that is 90% different from primers and cutSite
        for sequence in sequenceList:
            randomDNAEnd = getRandomDNAEnd(randomDNALength)
            while randomDNAEnd.find(fwd) is True or randomDNAEnd.find(rvs) is True:
                randomDNAEnd = getRandomDNAEnd(randomDNALength)
            DNASeq = reverse_translate(sequence[3:17])
            while DNASeq.find(fwd) is True or DNASeq.find(rvs) is True:
                DNASeq = reverse_translate(sequence[3:17])
            seqForChip = fwd + cut1 + DNASeq + 'TT' + cut2 + rvs + randomDNAEnd
            dictOutput['DNA Sequence'].append(seqForChip)
            dictOutput['Segment Number'].append(segmentNum)
            dictOutput['TM Sequence'].append(sequence[3:18])
        while gpaSeq.find(fwd) is True or gpaSeq.find(rvs) is True:
            gpaSeq = reverse_translate(gpa)
        while g83ISeq.find(fwd) is True or g83ISeq.find(rvs) is True:
            g83ISeq = reverse_translate(g83I)
        gpaDNASeq = fwd + cut1 + gpaSeq + 'AC' + cut2 + rvs + randomDNAEnd
        g83IDNASeq = fwd + cut1 + g83ISeq + 'AC'+ cut2 + rvs + randomDNAEnd
        i=0
        # At end of segment, add in the control sequences with a function
        for i in range(0,5):
            dictOutput['DNA Sequence'].append(gpaDNASeq)
            dictOutput['DNA Sequence'].append(g83IDNASeq)
            dictOutput['Segment Number'].append(segmentNum)
            dictOutput['Segment Number'].append(segmentNum)
            dictOutput['TM Sequence'].append(gpa)
            dictOutput['TM Sequence'].append(g83I)
            i+=1
    outputDf = pd.DataFrame.from_dict(dictOutput)
    return outputDf

# Local Variables
if __name__ == "__main__":
    input_file = sys.argv[1]
    output_dir = sys.argv[2]
    output_file = sys.argv[3]
    primer_file = sys.argv[4]

    # make the output directory if it doesn't exist
    os.makedirs(name=output_dir, exist_ok=True)
    # define the output file name from the input file name
    output_file = f'{output_dir}/{output_file}.xlsx'
    #inputFile = "C:\\Users\\gjowl\\Documents\\Senes Lab\\Design Research\\Sequence Design\\Analysis\\2022_1_5_CHIP\\CHIP1_Segments.xlsx"
    #outputDir = "C:\\Users\\gjowl\\Documents\\Senes Lab\\Design Research\\Sequence Design\\Analysis\\"
    #inputFile = outputDir + 'optimizedBackboneAnalysis.xlsx'
    #primerFile = "C:\\Users\\gjowl\\Downloads\\Primers.csv"
    #outputFile = outputDir + 'CHIP.xlsx'
    writer = pd.ExcelWriter(output_file)
    cutSite1 = 'gctagc'
    cutSite2 = 'gatc'
    gpa = 'LIIFGVMAGVIG'#final T comes from one of the base pairs in annealed cutsite, so hardcoded the codon for T
    g83I = 'LIIFGVMAIVIG'
    # after this is working properly, add in the 10 controls as a list
    randomDNALength = 21 #matches the number from Samantha's CHIP4
    seed = 1
    rand.seed(seed)

    # Main
    # Read in CHIP primer file
    dfPrimer = pd.read_csv(primer_file, sep=',')

    # Separate Primers and primer names and add to corresponding dataframes
    dfForwardPrimer = dfPrimer.iloc[0::2]
    dfReversePrimer = dfPrimer.iloc[1::2]
    dfForwardPrimer = dfForwardPrimer.reset_index()
    dfReversePrimer = dfReversePrimer.reset_index()
    dfForwardPrimer.pop('index')
    dfReversePrimer.pop('index')

    # read in the input file as a dataframe csv
    df_CHIP_seqs = pd.read_csv(input_file, sep=',')
    # remove any redundant sequences that may have been added as mutants
    df_CHIP_seqs = df_CHIP_seqs.drop_duplicates(subset=['Sequence'], keep='first')

    # nucleic acid sequences for gpa and g83I
    gpaSeq = reverse_translate(gpa)
    g83ISeq = reverse_translate(g83I)

    # convert AA sequences to DNA sequences and
    dfCHIP = getCHIPFile(df_CHIP_seqs, dfForwardPrimer, dfReversePrimer, gpaSeq, g83ISeq, cutSite1, cutSite2, randomDNALength)
    print(len(dfCHIP))
    # remove any redundant sequences that have same interface but different design ends
    dfCHIP = dfCHIP.drop_duplicates(subset=['TM Sequence'], keep='first')
    print(len(dfCHIP))
    writeDataframeToSpreadsheet(dfCHIP, writer, 'CHIP')

    writer.close()
