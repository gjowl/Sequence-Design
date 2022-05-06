import re
from dnachisel.biotools import translate, reverse_complement

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
    dnaSeqs = lines[1::4]
    qCodes = lines[3::4]
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
            i += 1
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

# OUTPUT SEQUENCE DICTIONARY
# convert DNA to protein sequence
def convertDNAToProtein(f, r, seq, offset, noEnd, direction):
    # Get sequence in between primers
    f += offset
    # this gets me the correct sequence to translate (for some reason SMA perl script skips first letter in translation?)
    tm = seq[f+1:r]
    protein = ''
    try:
        #tm = reverse_complement(tm)
        protein = translate(tm, assume_start_codon=True)
    except:
        noEnd += 0
    # TODO: haven't checked if this works yet
    if direction == "R":
        tm_complement = reverse_complement(tm)
        protein = translate(tm_complement)
    return protein

# get the qFactor to help determine if good sequence
def getQFactor(qCode):
    #Q = the Q factor given by the sequencing results (Higher is better)
    q = 0
    #P = the estimated probability of incorrect base in a seq (Lower is better)
    #P = 10^(-Q/10)
    p = 0
    tm = ''
    eIncorrect = 0
    # gets rid of any empty space at the end of the string
    qCode = qCode.strip()
    # I think this is for character in line
    for char in qCode: 
       # get ASCII value of character
       q = ord(char)-33
       # calculation?
       p = 10**(-q/10)
       eIncorrect += p
    return eIncorrect

# output a dictionary of good sequences
def getGoodSequences(dnaSeqs, qCodes, fPrimer, rPrimer, direction):
    proteinSeqs = {}
    poorSeq = 0
    noStart = 0
    noEnd = 0
    # loop through sequences and qcodes to add to dictionary
    for seq, qCode in zip(dnaSeqs, qCodes):
        eIncorrect = getQFactor(qCode)
        if eIncorrect > 1:
            poorSeq += 1
            continue
        # if either primer is not found in the sequence, skip
        try:
            f = seq.index(fPrimer)
            try:
                r = seq.index(rPrimer)
            except:
                noEnd += 1
                continue
        except:
            noStart += 1
            continue
        primerLength = len(fPrimer)
        if direction == "R":
            primerLength = len(rPrimer)
        # convert DNA to protein
        protein = convertDNAToProtein(f, r, seq, primerLength, noEnd, direction)
        
        # check to see if AS at the start of sequence
        if protein.find("AS", 0, 2) == -1:
            noStart += 1
            continue
        #check to see if L at end of sequence
        elif protein.endswith("L") == False:
            noEnd += 1
            continue
        else:
            # remove first AS and end L
            protein = protein[2:-1]
        if protein in proteinSeqs:
            proteinSeqs[protein] += 1
        else:
            proteinSeqs[protein] = 1
    return proteinSeqs, poorSeq, noStart, noEnd