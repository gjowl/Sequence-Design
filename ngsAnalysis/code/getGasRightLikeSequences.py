import sys
from functions import *

"""
Run as:
    python3 getGasRightLikeSequences.py [energyFile]

This converts a dataframe of energy files for my designed sequences into a 
csv file that contains only GASRight like sequences. I've noticed that many
of my sequences seem to be similar to GASright, and because of this I think
that it could be possible that my sequences have alternate dimerization modes,
which could be the reason for some having a higher amount of fluorescence than
the predicted energy. I'll take these sequences and run them through CATM and
see if there is better correlation between the CATM energy scores and the 
fluorescence. I was reading in an energy file and searching the 'Sequence'
column for matching GASright patterns.
"""
# checks for existence of a pattern where middle letters can be anything (GxxxG where x is any other letter)
# If you wanted to doll this up, could add in that it checks to make sure that the alphabet in the sequence
# is made up of only the 21 AAs
def checkForPatternBySepLength(df, colToCheck, matchingStringList, sepLength):
    df_output = pd.DataFrame()
    for string in df[colToCheck]:
        i = 0
        iterationLength = len(string)-sepLength
        while i < len(string)-sepLength:
            # get first letter of pattern
            first = string[i]
            last = string[i+sepLength]
            if (first in matchingStringList) and (last in matchingStringList):
                row = df[df[colToCheck] == string]
                df_output = pd.concat([df_output, row])
                i = iterationLength
            # iterate to the next number
            i+=1
    return df_output

#MAIN
# read in file from command line 
inputFile = sys.argv[1]
df = pd.read_csv(inputFile)
separationLength = int(sys.argv[2])

# variables
currentDir = os.getcwd()
outputFile = currentDir+'/gxxxgDesigns.csv'
gxxxgLetters = ['G','A','S']
col = 'Sequence'

# get just the matching sequences
df_match = checkForPatternBySepLength(df, col, gxxxgLetters, separationLength)

# output the matching sequence dataframe in csv format
df_match.to_csv(outputFile, index=False)

# output non matching sequences in csv format
df_nonGxxxg = df[df['Sequence'].isin(df_match['Sequence']) == False]
df_nonGxxxg.to_csv(currentDir+'/nonGxxxg.csv', index=False)

# gets only the design sequences that have a GASright like pattern
col = 'StartSequence'
df_match = checkForPatternBySepLength(df, col, gxxxgLetters, separationLength)

# get any sequences match the starting sequence
df_startGxxxG = df[df['StartSequence'].isin(df_match['StartSequence']) == True]
df_startGxxxG.to_csv(currentDir+'/startSeqGxxxg.csv', index=False)

# get all sequences that don't have a GxxxG starting sequence
df_noStartGxxxG = df[df['StartSequence'].isin(df_match['StartSequence']) == False]
df_noStartGxxxG.to_csv(currentDir+'/noStartSeqGxxxg.csv', index=False)

# TODO: get all sequences that have GxxxG but not started as GASright
df_nonStartGxxxg = df[df['Sequence'].isin(df_match['Sequence']) == False]
df_nonStartGxxxg.to_csv(currentDir+'/nonGxxxg.csv', index=False)

