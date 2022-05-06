import re
from dnachisel.biotools import reverse_translate

# load in NGS file
def readNGSFile(ngsFile):
    # create file object
    f = open(ngsFile,"r")
    # read all lines
    lines = f.readlines()
    """
    NGS File Format
    Each entry has 4 lines:
    Label
	    @M01987:419:000000000-BKRPV:1:1101:14644:1644 1:N:0:TAGACCGA+TAGACCGA
    Sequence
	    AAGGTGGGCTCCAAACTTGGGGAATCGAGCTAGCCTCATTATTTTTGGGGTGATGGCTGGTGTTATTGGAACGATCCTGATCAACCCAAGCCAATCCTTCCAGATCGGAAGAGCACACGTCTGAACTCCAGTCACTAGACCGAATCTCGTA
    Something....
        +
    Q Codes
	    1>>?AB?@>FAAF1DGGGFFCCCFHHFCFFF1FFGHHBGGBGHHHHCCCCFEEHFGFHGCHGHGBGHHGFEGECGHFHHBGHFGHFECCAFGEFGGFHHH0BFFGHGCCEEEFHHHGFGHHHGGHHHHHHFHHGHHBGFHHG?/F/GHFF.
    """
    # get only sequences and q codes (i.e. line[start:end:step]; keep sequence and Q codes)
    dnaSeqs = lines[1::3]
    qCodes = lines[3::3]
    # number of sequences
    return dnaSeqs, qCodes

# load a file with reference sequences and other information
def readReferenceFile(refFile):
    #get file object
    f = open(refFile, "r")
    #read all lines
    lines = f.readlines()
    #setup output dictionary
    dictSequence = {}
    #traverse through lines one by one
    for line in lines:
        lineSplit = re.split(r'\t', line.strip())
        seqInfo = ''
        i = 0 
        while i < 6:
            seqInfo += lineSplit[i] #TODO: split
            i = i+1
        seqName = lineSplit[6]
        dictSequence[seqName] = seqInfo 
    #close file
    f.close
    return dictSequence

def writeOutputFile(ngsFile, direction):
    print(ngsFile + " " + direction)
    
def reverseStrings(strings):
    revStrings = []
    for string in strings:
        revString.append(string[::-1])
    return revStrings