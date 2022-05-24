import re
import os
import sys
import pandas as pd
from dnachisel.biotools import translate, reverse_complement

def getConfigFile(file):
    configFile = ''
    # Access the configuration file for this program (should only be one in the directory)
    programPath = os.path.realpath(file)
    programDir, programFile = os.path.split(programPath)
    programName, programExt = os.path.splitext(programFile)
    fileList = os.listdir(programDir)
    for file in fileList:
        fileName, fileExt = os.path.splitext(file)
        if fileExt == '.config':
            configFile = programDir + '/' + file
    if configFile == '':
        sys.exit("No config file present in script directory!")
    return configFile

# get filename separate from type and directory
def getFilename(file):
    programPath = os.path.realpath(file)
    programDir, programFile = os.path.split(programPath)
    filename, programExt = os.path.splitext(programFile)
    return filename

def makeOutputDir(outputDir):
    # check if the path to the directory exists
    if not os.path.isdir(outputDir):
        print('Creating output directory: ' + outputDir + '.')
        # the below makes directories for the entire path
        os.makedirs(outputDir)
    else:
        print('Output Directory: ' + outputDir + ' exists.')

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

def reverseStrings(strings):
    revStrings = []
    for string in strings:
        revStrings.append(string[::-1])
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

# converts ngs fastq files to more workable txt files
def convertFastqToTxt(fastqTotxt, config, refFile, dataDir, outputDir):
    if len(os.listdir(outputDir)) == 0:
        for filename in sorted(os.listdir(dataDir)):
            dataFile = os.path.join(dataDir, filename)
            # confirms that file is a fastq
            if os.path.isfile(dataFile) and 'fastq' in dataFile:
                dataFile = dataFile.replace(" ", "\ ") # replaces spaces so that directories with spaces can be located by linux command line
                # gets the direction 
                if dataFile.find("R1") != -1:
                    name = getFilename(dataFile)
                    if 'C' in name:
                        name = name[0:7]
                    else:
                        name = name[0:11]
                    # TODO: work on naming these rather than switching everytime
                    #execRunFastqTotxt = 'perl seqNgsAnalysis-GJLedit.pl --refFile '+refFile+' --seqFile '+dataFile+' --direction 1 > '+outputDir+name+'.txt'
                    execRunFastqTotxt = 'perl AllSeqNgsAnalysis_CHIP.pl --refFile '+refFile+' --seqFile '+dataFile+' --direction 1 > '+outputDir+name+'.txt'
                    #execRunFastqTotxt = 'perl AllSeqNgsAnalysis_CHIP.pl --refFile /mnt/c/Users/gjowl/github/Sequence-Design/ngsAnalysis/2022-5-13/CheatRefSeqs.csv --seqFile '+dataFile+' --direction 1 > '+outputDir+name+'.txt'
                    # The below is using my version of the code
                    #execRunFastqTotxt = 'python3 '+fastqTotxt+' '+config+' '+dataFile+' '+'F'
                    print(execRunFastqTotxt)
                    os.system(execRunFastqTotxt)
                    eis()
                else:#TODO: get this working for reverse
                    continue
                    execRunFastqTotxt = 'python3 '+fastqTotxt+' '+config+' '+dataFile+' '+'R'
                    print(execRunFastqTotxt)
                    os.system(execRunFastqTotxt)
        print("Files successfully converted")
    else:
        print("Files already converted. If you would like to reconvert files, delete " + outputDir)

# FOR CREATING A CSV FILE OF SEQUENCE COUNTS PER BIN/M9/LB
#Checking the file exists or not
def check_file_empty(path_of_file):
    #Checking if file exist and it is empty
    return os.path.exists(path_of_file) 

def getCountsForFile(listSeq, dictSeq, colName, file):
    # convert to csv and keep the sequence, count, and percentage columns
    columns = ['Sequence', 'Count', 'Percentage']
    dfData = pd.read_csv(file, delimiter='\t', header=None, skiprows=4, usecols=[0,1,2])
    dfData.columns = columns
    # loop through all of the sequences and find count in dataframe
    for seq in listSeq:
        if seq not in dictSeq:
            dictSeq[seq] = {}
        # get data for the sequence in this file; if not found in file, set count as 0
        try:
            # search for the sequence as an index and get the count
            index = dfData.index[dfData['Sequence'] == seq].to_list()
            count = dfData.loc[index[0], 'Count']
            dictSeq[seq][colName] = count
        except:
            # if not found, set number for bin as 0
            dictSeq[seq][colName] = 0
    return dictSeq

def outputSequenceCountsCsv(listSeq, dir, outFile):
    dictSeq = {}
    # checking if file exist and it is empty
    fileExists = check_file_empty(outFile)
    if fileExists == False:
        for filename in sorted(os.listdir(dir)):
            # get one data file
            dataFile = os.path.join(dir, filename)
            # make sure it's a file
            if os.path.isfile(dataFile):
                # get the column name for this data from the file name (bin name, M9, LB, etc.)
                colName = getFilename(filename)
                dictSeq = getCountsForFile(listSeq, dictSeq, colName, dataFile)
        df = pd.DataFrame.from_dict(dictSeq)
        # transpose the dataframe so sequences are rows and bins and others are columns
        df_t = df.T
        df_t = df_t[sorted(df_t.columns)]
        df_t.to_csv(outFile)
    else:
        print("File exists. To rerun, delete " + outFile)

# get percents for each of the files
def getPercentsForFile(listSeq, dictSeq, colName, file):
    # convert to csv and keep the sequence, count, and percentage columns
    columns = ['Sequence', 'Count', 'Percentage']
    dfData = pd.read_csv(file, delimiter='\t', header=None, skiprows=4, usecols=[0,1,2])
    dfData.columns = columns
    # loop through all of the sequences and find count in dataframe
    for seq in listSeq:
        if seq not in dictSeq:
            dictSeq[seq] = {}
        # get data for the sequence in this file; if not found in file, set count as 0
        try:
            # search for the sequence as an index and get the count
            index = dfData.index[dfData['Sequence'] == seq].to_list()
            percent = dfData.loc[index[0], 'Percentage']
            dictSeq[seq][colName] = percent
        except:
            # if not found, set number for bin as 0
            dictSeq[seq][colName] = 0
    return dictSeq

# output percents as a csv
def outputSequencePercentsCsv(listSeq, dir, outFile):
    dictSeq = {}
    # checking if file exist and it is empty
    fileExists = check_file_empty(outFile)
    if fileExists == False:
        for filename in sorted(os.listdir(dir)):
            # get one data file
            dataFile = os.path.join(dir, filename)
            # make sure it's a file
            if os.path.isfile(dataFile):
                # get the column name for this data from the file name (bin name, M9, LB, etc.)
                colName = getFilename(filename)
                dictSeq = getPercentsForFile(listSeq, dictSeq, colName, dataFile)
        df = pd.DataFrame.from_dict(dictSeq)
        # transpose the dataframe so sequences are rows and bins and others are columns
        df_t = df.T
        df_t = df_t[sorted(df_t.columns)]
        df_t.to_csv(outFile)
    else:
        print("File exists. To rerun, delete " + outFile)
        
