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

def getCHIPFile(df, dfFwdP, dfRevP, cut1, cut2, randomDNALength):
    dictOutput = {}
    colNames = ['Segment Number', 'TM Sequence', 'DNA Sequence', 'Name', 'Owner']
    addColumnsToDictionary(dictOutput, colNames)
    for segmentNum in df['Segment'].unique():
        dfSegment = df[df['Segment'] == segmentNum]
        sequenceList = dfSegment["Sequence"]
        
        # get the current segment owner
        owner = dfSegment['Owner'].values[0]
        fwd, rvs = getPrimerSet(dfFwdP, dfRevP, segmentNum)
        # For every sequence, make a random string that is 90% different from primers and cutSite
        for sequence in sequenceList:
            # get the current sequence sample name
            sampleName = dfSegment[df["Sequence"] == sequence]['Name'].values[0]
            randomDNAEnd = getRandomDNAEnd(randomDNALength)
            while randomDNAEnd.find(fwd) is True or randomDNAEnd.find(rvs) is True:
                randomDNAEnd = getRandomDNAEnd(randomDNALength)
            DNASeq = reverse_translate(sequence[:17])
            while DNASeq.find(fwd) is True or DNASeq.find(rvs) is True:
                DNASeq = reverse_translate(sequence[:17])
            seqForChip = fwd + cut1 + DNASeq + 'TT' + cut2 + rvs + randomDNAEnd
            dictOutput['DNA Sequence'].append(seqForChip)
            dictOutput['Segment Number'].append(segmentNum)
            dictOutput['TM Sequence'].append(sequence[:18])
            dictOutput['Name'].append(sampleName)
            dictOutput['Owner'].append(owner)
    outputDf = pd.DataFrame.from_dict(dictOutput)
    return outputDf

# Local Variables
if __name__ == "__main__":
    primer_file = sys.argv[1]
    output_dir = sys.argv[2]
    output_file = sys.argv[3]
    # get the sequence files from the command line as a list
    sequence_files = sys.argv[4:]

    # make the output directory if it doesn't exist
    os.makedirs(name=output_dir, exist_ok=True)
    # define the output file name from the input file name
    output_file = f'{output_dir}/{output_file}'
    #inputFile = "C:\\Users\\gjowl\\Documents\\Senes Lab\\Design Research\\Sequence Design\\Analysis\\2022_1_5_CHIP\\CHIP1_Segments.xlsx"
    #outputDir = "C:\\Users\\gjowl\\Documents\\Senes Lab\\Design Research\\Sequence Design\\Analysis\\"
    #inputFile = outputDir + 'optimizedBackboneAnalysis.xlsx'
    #primerFile = "C:\\Users\\gjowl\\Downloads\\Primers.csv"
    #outputFile = outputDir + 'CHIP.xlsx'
    cutSite1 = 'gctagc'
    cutSite2 = 'gatc'

    randomDNALength = 21 #matches the number from Samantha's CHIP4
    seed = 1
    rand.seed(seed)

    # Read in CHIP primer file
    dfPrimer = pd.read_csv(primer_file, sep=',')

    # Separate Primers and primer names and add to corresponding dataframes
    dfForwardPrimer = dfPrimer.iloc[0::2]
    dfReversePrimer = dfPrimer.iloc[1::2]
    dfForwardPrimer = dfForwardPrimer.reset_index()
    dfReversePrimer = dfReversePrimer.reset_index()
    dfForwardPrimer.pop('index')
    dfReversePrimer.pop('index')

    # read in the input files as dataframes
    df_CHIP_seqs = pd.DataFrame()
    for input_file in sequence_files:
        input_df = pd.read_csv(input_file, sep=',')
        # output the duplicate sequence
        duplicate_seqs = input_df[input_df.duplicated(subset=['Sequence'], keep='first')]
        print(f'The following sequences are duplicated in {input_file}:')
        print(duplicate_seqs)
        # remove redundant sequences
        input_df = input_df.drop_duplicates(subset=['Sequence'], keep='first')
        # concat the input dataframes into one dataframe
        df_CHIP_seqs = pd.concat([df_CHIP_seqs, input_df], ignore_index=True)
    print(len(df_CHIP_seqs))

    # convert AA sequences to DNA sequences and
    dfCHIP = getCHIPFile(df_CHIP_seqs, dfForwardPrimer, dfReversePrimer, cutSite1, cutSite2, randomDNALength)
    # reset the index and remove the old index column
    dfCHIP = dfCHIP.reset_index()
    dfCHIP.pop('index')
    print(len(dfCHIP))

    # organization of the dataframe
    # add 1 to all segment numbers
    dfCHIP['Segment Number'] = dfCHIP['Segment Number'] + 1
    # move the name and owner columns to the front after segment number
    cols = dfCHIP.columns.tolist()
    cols = cols[0:2] + cols[-2:] + cols[2:-2]
    dfCHIP = dfCHIP[cols]
    # write the dataframe to a csv file
    #dfCHIP = dfCHIP.sort_values(by='Segment Number')
    dfCHIP.to_csv(output_file, sep=',', index=False)

    # write the dataframe to a csv file
    # sort by segment number
    #df_CHIP_seqs = df_CHIP_seqs.sort_values(by=['Segment Number', 'Owner'])
    #df_CHIP_seqs = df_CHIP_seqs.sort_values(by='Segment Number')
    #df_CHIP_seqs.to_csv(output_file, sep=',', index=False)