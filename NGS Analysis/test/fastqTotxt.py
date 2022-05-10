import sys
from functions import *

# Command line arguments
#TODO: change this to config file options
refFile = sys.argv[1]
ngsFile = sys.argv[2]
direction = sys.argv[3]
outputName = getFilename(ngsFile)
outputFile = outputName+"-test.txt"
#maybe add another argument for M9 vs sorted (so that I can add column names to the output file? Should I make it a csv also?)

# Control protein sequences
gpa = 'LIIFGVMAGVIG'
g83I = 'LIIFGVMAIVIG'

#Set the forward and reverse primers DNA sequences for forward NGS sequence
fPrimer = "GGCTCCAAACTTGGGGAATCG"
rPrimer = "CCTGATCAACCCAAGCCAATCC"
primers = [fPrimer, rPrimer]

#Reverse the primer string if analyzing the reverse NGS sequence
if direction == "R":
    primers = reverseStrings(primers)

# load in NGS file and get DNA sequence and qcodes
dnaSeqs, qCodes = readNGSFile(ngsFile)

# Output the sequence dictionary and information about good and bad sequences
proteinSeqs, poorSeq, noStart, noEnd = getGoodSequences(dnaSeqs, qCodes, fPrimer, rPrimer, direction)
totalSeqs = len(dnaSeqs)
goodSeq = totalSeqs-poorSeq-noStart-noEnd #TODO: just get the number of keys in proteinSeqs?
goodPercent = goodSeq/totalSeqs
#TODO: my noStart is off by like 40 for some reason? I'm getting rid of extra good sequences
sequenceOutput = "TotalSeqs PoorSeqs NoStart NoEnd GoodSeqs Percent\n"
sequenceOutput = sequenceOutput+str(totalSeqs)+" "+str(poorSeq)+" "+str(noStart)+" "+str(noEnd)+" "+str(goodSeq)+" "+str(goodPercent)+"\n"

# define the cutoff
cutoff = 10
writeOutputFile(proteinSeqs, totalSeqs, sequenceOutput, cutoff, refFile, outputFile)

#TODO: sort sequences (?)
# so even though my noStart is incorrect, it looks like I do output the same amount of sequences (same number of lines in my output file and Samantha's output)
# so I think I'm good