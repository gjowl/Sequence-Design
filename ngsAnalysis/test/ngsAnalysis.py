import sys
import helper
from functions import *
from ngsAnalysisFunctions import *

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
inputDir        = config["inputDir"]

# make the output directory that these will all output to
makeOutputDir(outputDir)

# read csv containing counts
df = pd.read_csv(countFile)

# filter out to only have the bins
# get the first column (sequence column)
seqs = df.iloc[:,0]
# filter for bins, LB, and M9
ids = df.iloc[:,1]
# filter for bins, LB, and M9
dfBins = df.filter(like='C')
dfLB = df.filter(like='LB')
dfM9 = df.filter(like='M9')

# filter out to only have Rep1
numReplicates = 3
dfFlow = pd.read_csv(flowFile, index_col=0)
i=1
dfAvgGood = pd.DataFrame()
dfAvgTotal = pd.DataFrame()
while i <= numReplicates:
    replicate = 'Rep'+str(i)
    dfRep = dfBins.filter(like=replicate)
    # get all bin names
    bins = dfRep.columns
    # add in sequence column to first column, then as index
    dfRep.insert(0, 'Sequence', seqs)
    dfRep = dfRep.set_index('Sequence')
    # get a dataframe with numerators and denominators
    dfGoodNumDenom, dfTotalNumDenom = calculateNumeratorsAndDenominators(seqs, inputDir, bins, dfRep, dfFlow)
    # output a dataframe of a values for each sequence for each bin
    dfNormGood, dfNormTotal = calculateNormalizedSequenceContribution(bins, dfGoodNumDenom, dfTotalNumDenom)
    filename = outputDir+'norm'+replicate+'.csv'
    dfNormGood.to_csv(filename)
    # calculate the final reconstructed fluorescence
    dfFluorGood, dfFluorTotal = calculateReconstructedFluorescence(bins, dfNormGood, dfNormTotal, dfFlow)
    dfFluorGood.insert(0,'Sequence',seqs)
    # write to output file for each replicate
    filename = outputDir+replicate+'Good.csv'
    dfFluorGood.to_csv(filename)
    filename = outputDir+replicate+'Total.csv'
    dfFluorTotal.to_csv(filename)
    # add to dataframe that will be used to analyze fluorescence
    fluorGoodCol = dfFluorGood['Fluorescence']
    dfAvgGood.insert(i-1, replicate+'-Fluor', fluorGoodCol)
    fluorTotalCol = dfFluorTotal['Fluorescence']
    dfAvgTotal.insert(i-1, replicate+'-Fluor', fluorTotalCol)
    i+=1

# get average, stDev, etc. from reconstructed fluorescence
dfAvgGood = outputReconstructedFluorescenceDf(dfAvgGood)
dfAvgTotal = outputReconstructedFluorescenceDf(dfAvgTotal)

# output dataframe to csv file 
filename = outputDir+'avgFluorGoodCounts.csv' # TODO: make into a config option
dfAvgGood.insert(0, 'Sequence', seqs)
dfAvgGood.insert(1, 'Ids', ids)
dfAvgGood.to_csv(filename)
filename = outputDir+'avgFluorTotalCounts.csv' # TODO: make into a config option
dfAvgTotal.insert(0, 'Sequence', seqs)
dfAvgTotal.insert(1, 'Ids', ids)
dfAvgTotal.to_csv(filename)