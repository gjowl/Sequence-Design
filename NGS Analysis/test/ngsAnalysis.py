import sys
from functions import *

# Command line arguments
refFile = sys.argv[1]
ngsFile = sys.argv[2]
direction = sys.argv[3]

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

# read in sequence reference file into dictionary (i.e. dict[seqName]=sequenceInfo)
dictRef = readReferenceFile(refFile)

# load in NGS file and get DNA sequence and qcodes
dnaSeqs, qCodes = readNGSFile(ngsFile)

# Output the sequence dictionary and information about good and bad sequences
proteinSeqs, poorSeq, noStart, noEnd = getGoodSequences(dnaSeqs, qCodes, fPrimer, rPrimer, direction)
totalSeqs = len(dnaSeqs)
goodSeq = totalSeqs-poorSeq-noStart-noEnd #TODO: just get the number of keys in proteinSeqs?
goodPercent = goodSeq/totalSeqs
#TODO: my noStart is off by like 40 for some reason? I'm getting rid of extra good sequences
print("TotalSeqs PoorSeqs NoStart NoEnd GoodSeqs Percent")
print(totalSeqs, poorSeq, noStart, noEnd, goodSeq, goodPercent)

cutoff = 10
#basically correct, but the percentage is calculated wrong? I'll need to determine why that is the case later
for seq, numSeq in proteinSeqs.items():
    if numSeq > cutoff:
        percent = numSeq/totalSeqs
        print(seq, numSeq, percent)
        if seq in dictRef:
            print(dictRef[seq])
        elif seq == gpa:
            print("0\tP02724\tGLPA_HUMAN\t75\tWT\tN/A\n")
        elif seq == g83I:
            print("0\tP02724\tGLPA_HUMAN\t75\tG83I\t83\n")
        else:
            print("unknown")
        exit()



#TODO: sort sequences (?)
#TODO: set a cutoff for the number of sequences we will analyze (?)
#TODO: output file similar to her output