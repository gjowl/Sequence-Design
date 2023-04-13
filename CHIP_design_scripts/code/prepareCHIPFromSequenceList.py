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
    fwdPrimer = dfFwd['Fwd'][row]
    revPrimer = dfRvs['Rvs'][row]
    return fwdPrimer, revPrimer

def getRandomDNAEnd(length):
    randSeq = ""
    DNA = ['g', 'a', 't', 'c']
    while len(randSeq) < length:
        randSeq = randSeq+rand.choice(DNA)
    return randSeq

def getCHIPFile(df, dfFwdP, dfRevP, df_controls, cut1, cut2, randomDNALength):
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
            DNASeq = reverse_translate(sequence[:14])
            while DNASeq.find(fwd) is True or DNASeq.find(rvs) is True:
                DNASeq = reverse_translate(sequence[:14])
            seqForChip = fwd + cut1 + DNASeq + 'TT' + cut2 + rvs + randomDNAEnd
            dictOutput['DNA Sequence'].append(seqForChip)
            dictOutput['Segment Number'].append(segmentNum)
            dictOutput['TM Sequence'].append(sequence[:15])
        # Add in the controls
        for control in df_controls['TM Sequence']:
            # get the DNA sequence for the control from the dataframe
            controlSeq = df_controls[df_controls['TM Sequence'] == control]['DNA Sequence'].values[0]
            while controlSeq.find(fwd) is True or controlSeq.find(rvs) is True:
                controlSeq = reverse_translate(control)
            controlDNASeq = fwd + cut1 + controlSeq + 'AC' + cut2 + rvs + randomDNAEnd
            i=0
            # At end of segment, add in the control sequences with a function
            for i in range(0,3):
                dictOutput['DNA Sequence'].append(controlDNASeq)
                dictOutput['Segment Number'].append(segmentNum)
                dictOutput['TM Sequence'].append(control)
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
    g83i = 'LIIFGVMAIVIG'

    # controls from Samantha's CHIP4 (?)
    P_1G02 = 'CAVVVGVGLIVGFAVGL'
    P_1C03 = 'VLGAAGTALLCAGLLLSLF'
    P_2H07 = 'IIVAMTAVGGSICVMLVVICL'
    P_2E06 = 'LALGLGACLLAGTSLSVLWVY'
    P_2H01 = 'FHMIAVGLSSSILGCLITLLV'
    #N_1E01 = 'FALGLGFCLPAGTSLSV'
    #N_1E11 = 'ILFVIAVASELGYFLCI'
    N_2E11 = 'VVIIAVVCCVVGTSLVWIVII'
    N_2F12 = 'VVIIAIVCCVVGTSLVWVVII'
    N_2H11 = 'GIYFVLGVCFGLLLTLCLLVI'

    # add in the controls as a list
    #controls = [gpa, g83i, P_1G02, P_1C03, P_2H07, P_2E06, P_2H01, N_1E01, N_1E11, N_2E11, N_2F12, N_2H11]
    controls = [gpa, g83i, P_1G02, P_1C03, P_2H07, P_2E06, P_2H01]

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
    print(len(df_CHIP_seqs))

    # nucleic acid sequences for gpa and g83I
    # get the list of nucleic acid sequences for the controls
    controlNucleicAcidSeqs = []
    for control in controls:
        controlNucleicAcidSeqs.append(reverse_translate(control))
    # add the nucleic acid sequences for the controls to the dataframe
    df_controls = pd.DataFrame(controls, columns=['TM Sequence'])
    df_controls['DNA Sequence'] = controlNucleicAcidSeqs

    # convert AA sequences to DNA sequences and
    dfCHIP = getCHIPFile(df_CHIP_seqs, dfForwardPrimer, dfReversePrimer, df_controls, cutSite1, cutSite2, randomDNALength)
    # reset the index and remove the old index column
    dfCHIP = dfCHIP.reset_index()
    dfCHIP.pop('index')
    print(len(dfCHIP))
    writeDataframeToSpreadsheet(dfCHIP, writer, 'CHIP')

    writer.close()
