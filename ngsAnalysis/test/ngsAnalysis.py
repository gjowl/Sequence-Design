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

