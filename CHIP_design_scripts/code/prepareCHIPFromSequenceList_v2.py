"""
This piece of code is for writing a csv file that can be used to purchase a CHIP, similar to Samantha's CHIP4.
  - Reads in the CHIP primer file to choose primers for segments (24 pairs of primers, so up to 24 segments can be made)
  - Extract a list of amino acid sequences from a DataFrame and converts it to nucleic acid sequences with proper cutsites and primers
  - Writes the output file for CHIP to be submitted to a vendor (TwistBiosciences or Agilent)

To Run:
python3 prepareCHIPFromSequenceList_v2.py -primer_file <primer_file> -control_file <control_file> -sequence_file <sequence_file> -output_dir <output_dir> -output_file <output_file>
    # necessary arguments
    - primer_file: The file containing the primer sequences
    - control_file: The file containing the control sequences # from Samantha's Thesis, page 116
    - sequence_file: The list of sequences
    # optional arguments
    - output_dir: The directory to save the output file
    - output_file: The name of the output file
"""
import os, sys, pandas as pd, re, argparse, numpy as np, matplotlib.pyplot as plt, random as rand, dnachisel
from datetime import date
from scipy import stats
from matplotlib import gridspec
from dnachisel.biotools import reverse_translate

# initialize the parser
parser = argparse.ArgumentParser(description='Prepare a CHIP file from a list of sequences')
# add the necessary arguments
parser.add_argument('-primer_file', type=str, help='The file containing the primer sequences')
parser.add_argument('-control_file', type=str, help='The file containing the control sequences')
parser.add_argument('-sequence_file', type=str, help='The list of sequences')
# add the optional arguments
parser.add_argument('-output_dir', type=str, help='The directory to save the output file')
parser.add_argument('-output_file', type=str, help='The name of the output file')

# parse the arguments
args = parser.parse_args()
primer_file = args.primer_file
control_file = args.control_file
sequence_file = args.sequence_file
# default the optional arguments
output_dir = os.getcwd()
output_file = f'{output_dir}/CHIP.csv'
if args.output_dir:
    output_dir = args.output_dir
    # make the output directory if it doesn't exist
    os.makedirs(name=output_dir, exist_ok=True)
if args.output_file:
    output_file = args.output_file
    # define the output file name from the input file name
    output_file = f'{output_dir}/{output_file}.csv'

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

def getCHIPFile(df, dfFwdP, dfRevP, df_controls, cut1, cut2, control_segments, randomDNALength):
    dictOutput = {}
    colNames = ['Segment Number', 'TM Sequence', 'DNA Sequence', 'SeqType']
    addColumnsToDictionary(dictOutput, colNames)
    for segmentNum in df['Segment'].unique():
        dfSegment = df[df['Segment'] == segmentNum]
        sequenceList = dfSegment["Sequence"]
        
        fwd, rvs = getPrimerSet(dfFwdP, dfRevP, segmentNum)
        # For every sequence, make a random string that is 90% different from primers and cutSite
        for sequence in sequenceList:
            # get the current sequence sample name
            sampleName = dfSegment[df["Sequence"] == sequence]['SeqType'].values[0]
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
            dictOutput['SeqType'].append(sampleName)
        # Add in the control
        if segmentNum in control_segments:
            for control in df_controls['TM Sequence']:
                # get the DNA sequence for the control from the dataframe
                controlSeq = df_controls[df_controls['TM Sequence'] == control]['DNA Sequence'].values[0]
                while controlSeq.find(fwd) is True or controlSeq.find(rvs) is True:
                    controlSeq = reverse_translate(control)
                # get the uniprot ID for the control from the dataframe
                uniprotID = df_controls[df_controls['TM Sequence'] == control]['Uniprot'].values[0]
                if uniprotID == 'GpA' or uniprotID == 'G83I':
                    controlDNASeq = fwd + cut1 + controlSeq + 'AC' + cut2 + rvs + randomDNAEnd
                else:
                    controlDNASeq = fwd + cut1 + controlSeq + 'TT' + cut2 + rvs + randomDNAEnd
                i=0
                # At end of segment, add in the control sequences with a function
                for i in range(0,3):
                    dictOutput['DNA Sequence'].append(controlDNASeq)
                    dictOutput['Segment Number'].append(segmentNum)
                    dictOutput['TM Sequence'].append(control)
                    dictOutput['SeqType'].append('Control')
                    i+=1
    outputDf = pd.DataFrame.from_dict(dictOutput)
    return outputDf

# Local Variables
cutSite1 = 'gctagc'
cutSite2 = 'gatc'

# hardcoded control segments list
control_segments = [1,2,3]

if __name__ == "__main__":
    # after this is working properly, add in the 10 controls as a list
    randomDNALength = 21 #matches the number from Samantha's CHIP4
    seed = 1
    rand.seed(seed)

    # open the controls file as a dataframe
    df_controls = pd.read_csv(control_file, sep=',')
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
    input_df = pd.read_csv(sequence_file, sep=',')
    # remove redundant sequences
    input_df = input_df.drop_duplicates(subset=['Sequence'], keep='first')
    # concat the input dataframes into one dataframe
    df_CHIP_seqs = pd.concat([df_CHIP_seqs, input_df], ignore_index=True)
    print(len(df_CHIP_seqs))

    # get the list of nucleic acid sequences for the controls
    controlNucleicAcidSeqs = []
    for control in df_controls['TM Sequence']:
        controlNucleicAcidSeqs.append(reverse_translate(control))
    df_controls['DNA Sequence'] = controlNucleicAcidSeqs

    # convert AA sequences to DNA sequences and
    dfCHIP = getCHIPFile(df_CHIP_seqs, dfForwardPrimer, dfReversePrimer, df_controls, cutSite1, cutSite2, control_segments, randomDNALength)
    # reset the index and remove the old index column
    dfCHIP = dfCHIP.reset_index()
    dfCHIP.pop('index')
    print(len(dfCHIP))

    # organization of the dataframe
    # add 1 to all segment numbers
    dfCHIP['Segment Number'] = dfCHIP['Segment Number'] + 1
    cols = dfCHIP.columns.tolist()
    cols = cols[0:2] + cols[-2:] + cols[2:-2]
    dfCHIP = dfCHIP[cols]
    # write the dataframe to a csv file
    #dfCHIP = dfCHIP.sort_values(by='Segment Number')
    dfCHIP.to_csv(output_file, sep=',', index=False)