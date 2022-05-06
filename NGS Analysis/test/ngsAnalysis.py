import sys
from functions import *




refFile = sys.argv[1]
ngsFile = sys.argv[2]
direction = sys.argv[3]
gpa = 'LIIFGVMAGVIG'
g83I = 'LIIFGVMAIVIG'

#Set the forward and reverse primers for forward NGS sequence
fPrimer = "GGCTCCAAACTTGGGGAATCG"
rPrimer = "CCTGATCAACCCAAGCCAATCC"
offset = 21
primers = [fPrimer, rPrimer]
#Flip the primer string if analyzing the reverse NGS sequence
if direction == "R":
    primers = reverseStrings(primers)
    offset = 22

# read in sequence reference file into dictionary (i.e. dict[seqName]=sequenceInfo)
dictRef = readReferenceFile(refFile)

# load in NGS file and get DNA sequence and qcodes
dnaSeqs, qCodes = readNGSFile(ngsFile)

#
#  
#TODO: set a cutoff for the number of sequences we will analyze (?)
#TODO: open the sequence file (fastq)
#   - set variables for looping
#   - loop through every line
poorSeq = 0
noStart = 0
noEnd = 0

#TODO: a lot to figure out below
for seq, q in zip(dnaSeqs, qCodes):
    # look up what this p calculation is doing and what split // is in perl
    for ...
        
    q = 0
    p = 0
    eIncorrect = 0
    tm = ''
    if eIncorrect > 1:
        poorSeq = poorSeq +1
        next #TODO: does next also work for python?

    # TODO: confirm that this is what perl is doing
    j = find(fPrimer, seq)
    k = find(rPrimer, seq)
    # TODO: what does crop good sequence in between primers mean?
    if (j == -1):
        noStart = noStart+1
        next
    j = j + offset
    if (k != -1):
        #TODO: how to get this TM using python? substr in perl?
        tm = ''
    else:
        noEnd = noEnd+1
        next

    # convert DNA to protein
    protein = reverse_translate(tm)

    # TODO: finish the rest of this for loop

    ...
#TODO: convert DNA to protein
#TODO: print out the total, good, bad, etc. sequences
#TODO: sort sequences (?)
#TODO: output file similar to her output