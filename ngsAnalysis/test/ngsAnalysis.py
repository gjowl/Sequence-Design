import sys
import helper
import statistics as stat
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

# read csv containing counts
df = pd.read_csv(countFile)

# filter out to only have the bins
# get the first column (sequence column)
seqs = df.iloc[:,0]
# filter for bins, LB, and M9
ids = df.iloc[:,1]
dfBins = df.filter(like='C')
dfLB = df.filter(like='LB')
dfM9 = df.filter(like='M9')

# filter out to only have Rep1
numReplicates = 3
# read in the file with data from sorting (median fluorescence and population fraction per bin)
dfFlow = pd.read_csv(flowFile, index_col=0)
# initialize dataframe to hold average and standard deviation
dfAvg = pd.DataFrame()
i=1
while i <= numReplicates:
    replicate = 'Rep'+str(i)
    dfRep = dfBins.filter(like=replicate)
    # get all bin names
    bins = dfRep.columns
    # add in sequence column to first column, then as index
    dfRep.insert(0, 'Sequence', seqs)
    dfRep.insert(1, 'Ids', ids)
    dfRep = dfRep.set_index('Sequence')
    # get a dataframe with numerators and denominators
    dfNumAndDenom = calculateNumeratorsAndDenominators(seqs, bins, dfRep, dfFlow)
    # output a dataframe of a values for each sequence for each bin
    dfNorm = calculateNormalizedSequenceContribution(bins, dfNumAndDenom)
    # calculate the final reconstructed fluorescence
    dfFluor = calculateReconstructedFluorescence(bins, dfNorm, dfFlow)
    dfFluor.insert(0,'Sequence',seqs)
    dfFluor.insert(1,'Ids',ids)
    # write to an output file for each replicate
    filename = outputDir+replicate+'.csv'
    dfFluor.to_csv(filename)
    # add to dataframe that will be used to analyze fluorescence
    fluorCol = dfFluor['Fluorescence']
    dfAvg.insert(i-1, replicate+'-Fluor', fluorCol)
    i+=1

# get average, stDev, etc. from reconstructed fluorescence
dfAvg = outputReconstructedFluorescenceDf(dfAvg)
# output dataframe to csv file 
filename = outputDir+'avgFluor.csv' # TODO: make into a config option
dfAvg.insert(0, 'Sequence', seqs)
dfAvg.insert(1, 'Ids', ids)
dfAvg.to_csv(filename)