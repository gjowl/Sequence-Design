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
    dfRepLB = dfLB.filter(like=replicate)
    dfRepM9 = dfM9.filter(like=replicate)
    # get all column names
    LBColNames = dfRep.columns
    M9ColNames = dfRep.columns
    # add in sequence column to first column, then as index
    dfRepLB.insert(0, 'Sequence', seqs)
    dfRepM9.insert(0, 'Sequence', seqs)
    dfRep = dfRep.set_index('Sequence')
    # calculate the ratio of sequences between LB and M9 media at different hour marks
    for seq in seqs: 
        for LBCol, M9Col in zip(LBColNames, M9ColNames):
            count = LBCol['Sequence'].at(seq)
            print(count)

    # write to output file for each replicate
    filename = outputDir+'LB-M9-'+replicate+'.csv'
    i+=1

# get average, stDev, etc. from reconstructed fluorescence
dfAvg = outputReconstructedFluorescenceDf(dfAvg)
# output dataframe to csv file 
filename = outputDir+'avgFluor.csv' # TODO: make into a config option
dfAvg.insert(0, 'Sequence', seqs)
dfAvg.to_csv(filename)