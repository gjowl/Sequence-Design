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
outputFile = currentDir+'/matchingSequences.csv'
gxxxgLetters = ['G','A','S']
col = 'Sequence'

# get just the matching sequences
df_match = checkForPatternBySepLength(df, col, gxxxgLetters, separationLength)

# set the matching column to the first column of the dataframe
first_column = df_match.pop(col)
df_match.insert(0, col, first_column)

# output the matching sequence dataframe in csv format
df_match.to_csv(outputFile, index=False)