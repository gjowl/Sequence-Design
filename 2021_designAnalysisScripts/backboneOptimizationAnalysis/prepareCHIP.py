# -*- coding: utf-8 -*-
# @Author: Gilbert Loiseau
# @Date:   2021-12-25
# @Last Modified by:   Gilbert Loiseau
# @Last Modified time: 2022-04-22 15:42:10
"""
This piece of code is for writing a csv file that can be used to purchase a CHIP, similar to Samantha's CHIP4.
  - Reads in the CHIP primer file to choose primers for segments (24 pairs of primers, so up to 24 segments can be made)
  - Extract a list of amino acid sequences from a DataFrame made by optimizedBackboneAnalysis and converts it to
    nucleic acid sequences with proper cutsites and primers
  - Writes the output file for CHIP to be submitted to a vendor (TwistBiosciences or Agilent)

TODO:
    - Write in a way to output the proper energies for each sequence
"""
import sys
import pandas as pd
import random as rand
from utilityFunctions import *
from dnachisel.biotools import reverse_translate
import helper
from prepareCHIPFunctions import *

# Use the utilityFunctions function to get the name of this program
programName = getProgramName(sys.argv[0])
configFile = sys.argv[1]

# Read in configuration file:
globalConfig = helper.read_config(configFile)
config = globalConfig[programName]

# Variables
outputDir = config["outputDir"]
inputFile = config["inputFile"]
primerFile = config["primerFile"]
outputFile = config["outputFile"]
seed = config["seed"]

# Setup
writer = pd.ExcelWriter(outputFile)
cutSite1 = 'gctagc'
cutSite2 = 'gatc'
gpa = 'LIIFGVMAGVIG'#final T comes from one of the base pairs in annealed cutsite, so hardcoded the codon for T
g83I = 'LIIFGVMAIVIG'
randomDNALength = 21 #matches the number from Samantha's CHIP4
rand.seed(seed)

# Main
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

# read excel spreadsheet with the randomly chosen CHIP sequences from optimizedBackboneAnalysis
dfAllSequences = pd.read_excel(inputFile, sheet_name='Segments')

# nucleic acid sequences for gpa and g83I
gpaSeq = reverse_translate(gpa)
g83ISeq = reverse_translate(g83I)

# convert AA sequences to DNA sequences and
dfCHIP = getCHIPFile(dfAllSequences, dfForwardPrimer, dfReversePrimer, gpaSeq, g83ISeq, cutSite1, cutSite2, randomDNALength)
writeDataframeToSpreadsheet(dfCHIP, writer, 'CHIP')

writer.close()
