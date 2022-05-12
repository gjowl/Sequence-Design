
# reconstructed fluorescence variables
"""
From input file
i = the sequence in AA format
j = current bin number
c = the number of a sequence counted within the bin

From sorter
f = fraction of the entire population (as a percent from sorting) found within the bin 
m = median fluorescence of the sorted bin

Reconstructed fluorescence
a = fluorescence in current bin
p = average fluorescence 
"""
import sys
import helper
from functions import *
# TODO: make a script that compiles the files into 1
# compile the files into one in below file format

# CSV file format:
# sequence bin1Count bin2Count bin3Count bin4Count bin5Count bin6Count totalCount fractionPop medianFluor
# TODO: how do I get the replicates for each of these?
# I think I got it:
#   - run the fastqToTxt on all
#   - compile those into a file that contains all bins and replicates
#   - hmmm...I think I just need to try it: 
#       - first get the sequence from a file and add to another file
#       - then add all of the other counts from individual files
#       - do it for all of the replicates
#       - sum them and add a column
#       - add fluor and fraction pop? Or just take from another file (loop through one then the other?)
# bin list (is there a way to get this? get only columns named bin)
#   - for loop through name
#       - for loop for bin in binlist for each name
#       - do the calculation of normFrac for each bin
#       - add previous normFrac to current
#   - calc relative fluor and output to a csv (plotting will be done in another script; maybe added on to this list of scripts)

# Use the utilityFunctions function to get the name of this program
programName = getFilename(sys.argv[0])
configFile  = sys.argv[1]

# Read in configuration file:
globalConfig = helper.read_config(configFile)
config = globalConfig[programName]

# Config file options:
countFile       = config["countFile"]
flowFile        = config["flowFile"]

# read csv containing counts
df = pd.read_csv(countFile)

# filter out to only have the bins
# get the first column (sequence column)
seqs = df.iloc[:,0]
# filter for bins, LB, and M9
dfBins = df.filter(like='C')
dfLB = df.filter(like='LB')
dfM9 = df.filter(like='M9')

# filter out to only have Rep1
numReplicates = 3
dfFlow = pd.read_csv(flowFile)

i=1
while i <= numReplicates:
    replicate = 'Rep'+str(i)
    dfRep = dfBins.filter(like=replicate)
    # get all bin names
    bins = dfRep.columns
    # get count of a single sequence in all bins
    totalSeqCounts = dfRep.sum(axis=1)
    # get total counts of all sequences in all columns/bins
    allSequenceInAllBinCount = dfRep.values.sum()
    for currBin in bins:
        # get total counts of all sequences in column/bin
        countSeqsInBin = dfRep[colName].sum(axis=0)
        print(countSeqsInBin)
        # get count of sequence
        for seq, count, totalSeqCount in zip(seqs,dfRep[currBin],totalSeqCounts):
            if count > 0:
                print(colName, count, seq, totalSeqCount)
                #this should give me all of the values I need from here
                # now just need to add in values from the flowFile (median and fraction pop)
                num = count/countSeqsInBin
                # I think I need a function to get denom: loop through all bins and getthese values
                denom = totalSeqCounts/allSequenceInAllBinCount
    i+=1
exit()


def calculateReconstructedFluorescence():
    for seq in binNumber:# maybe from outputfile with the name?
    #for seq in the outfile (I realized I don't have the proper output file (M9), 
    # so need to see if we can get bin number from the file)
    # from a csv, get the 
        calculateBinFluorescence(seq)
        m = median
        p = fluor

def calculateBinFluorescence(seq, binNumber, count):  
    i = seq
    j = binNumber
    c = count
    f = fract
    a = normFract

    # TODO: 
    # Summarize all sequence counts for a sequence
    # pull from a counts dictionary by sequence
    # pull from a bin counts dictionary by sequence
    # dictionary with all to dataframe, get the total, the count, and the fraction for each sequence
    num = f*ci
    denom = ci

    a = num/denom