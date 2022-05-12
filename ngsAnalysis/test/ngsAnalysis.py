
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

# FUNCTIONS 
def calcSeqProportionInBin(sequence, binName, dfRep, dfFlow):
    # get sequence count in bin
    seqCount = dfRep.loc[sequence][binName]
    # get total counts of all sequences in bin
    totalAllSeqCount = dfRep[binName].sum(axis=0)
    # get percent population in bin
    percent = dfFlow.loc['Percent'][binName]
    # calculate the sequence proportion for a single bin
    binValue = percent*seqCount/totalAllSeqCount
    return binValue

def calculateNumerators(seqs, binName, dfRep, dfFlow):
    allNums = []
    for seq in seqs:
        num = calcSeqProportionInBin(seq, binName, dfRep, dfFlow)
        allNums.append(num)
    return allNums

# loops through all sequences and all bins for that sequence and calculates the reconstructed fluorescence denominator
def calculateDenominators(seqs, bins, dfRep, dfFlow):
    allDenoms = []
    for seq in seqs:
        # denominator variable to hold for each sequence
        denom = 0
        for currBin in bins:
            # get sequence count in bin
            seqCount = dfRep.loc[seq][currBin]
            # get total counts of all sequences in bin
            totalAllSeqCount = dfRep[currBin].sum(axis=0)
            # get percent population in bin
            percent = dfFlow.loc['Percent'][currBin]
            # calculate the denominator for a single bin
            binValue = percent*seqCount/totalAllSeqCount
            # add to previous bin denominator total until calculated for all bins
            denom += binValue
        # append the calculated denominator to the allDenominator list
        allDenoms.append(denom)
    return allDenoms

def calculateNumeratorsAndDenominators(seqs, bins, dfRep, dfFlow):
    df = pd.DataFrame()
    # calculate the numerators
    for currBin in bins:
        binNumerators = calculateNumerators(seqs, currBin, dfRep, dfFlow)
        colName = currBin+'-Numerator'
        numColumns = len(df.columns)
        df.insert(numColumns, colName, binNumerators)
    # get the denominator for the equation 
    allDenominators = calculateDenominators(seqs, bins, dfRep, dfFlow)
    # I think I'm going to make this a new dataframe and print it out (with numerators, denominators, etc.)
    # add denominator to dataframe as a column under title Denominator
    df = df.assign(Denominator = allDenominators)
    return df

def calculateNormalizedSequenceContribution(bins, df):
    dfOut = pd.DataFrame()
    for colName, binName in zip(df.columns, bins):
        if colName != 'Denominator':
            dfOut[binName] = (df[colName]/df['Denominator'])
    return dfOut

def calculateReconstructedFluorescence(bins, dfNorm, dfFlow):
    df = pd.DataFrame()
    for binName in bins:
        median = dfFlow.loc['Median'][binName]
        df[binName] = (dfNorm[binName]*median)
    sumRows = df.sum(axis=1)
    df['Fluorescence'] = sumRows
    return df
# MAIN
# Use the utilityFunctions function to get the name of this program
programName = getFilename(sys.argv[0])
configFile  = sys.argv[1]

# Read in configuration file:
globalConfig = helper.read_config(configFile)
config = globalConfig[programName]

# Config file options:
countFile       = config["countFile"]
flowFile        = config["flowFile"]
outputDir       = config["outputDir"]

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
dfFlow = pd.read_csv(flowFile, index_col=0)
i=1
while i <= numReplicates:
    replicate = 'Rep'+str(i)
    dfRep = dfBins.filter(like=replicate)
    # get all bin names
    bins = dfRep.columns
    # add in sequence column to first column, then as index
    dfRep.insert(0, 'Sequence', seqs)
    dfRep = dfRep.set_index('Sequence')
    # get a dataframe with numerators and denominators
    dfNumAndDenom = calculateNumeratorsAndDenominators(seqs, bins, dfRep, dfFlow)
    # output a dataframe of a values for each sequence for each bin
    dfNorm = calculateNormalizedSequenceContribution(bins, dfNumAndDenom)
    # calculate the final reconstructed fluorescence
    dfFluor = calculateReconstructedFluorescence(bins, dfNorm, dfFlow)
    dfFluor.insert(0,'Sequence',seqs)
    # write to output file for each replicate
    filename = outputDir+replicate+'.csv'
    dfFluor.to_csv(filename)
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