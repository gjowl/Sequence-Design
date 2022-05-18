import sys
import helper
from functions import *
from ngsAnalysisFunctions import *

# get the name of this program and the input config gile
programName = getFilename(sys.argv[0])
configFile  = sys.argv[1]

# Read in configuration file for this program:
globalConfig = helper.read_config(configFile)
config = globalConfig[programName]

# Config file options:
countFile       = config["countFile"]
percentFile     = config["percentFile"]
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
# get the second column (id column)
ids = df.iloc[:,1]
# filter for bins, LB, and M9
dfBins = df.filter(like='C')
dfLB = df.filter(like='LB')
dfM9 = df.filter(like='M9')

# filter out to only have Rep1
numReplicates = 3
dfFlow = pd.read_csv(flowFile, index_col=0)
i=1

# if counts file exists, don't recreate
filename = outputDir+'avgFluorGoodCounts.csv' # TODO: make into a config option
fileExists = check_file_empty(filename)
if fileExists == False:
    df_good, df_total = getReconstructedFluorescenceDf(numReplicates, dfBins, seqs, inputDir, outputDir, dfFlow, usePercents=False)
    # output dataframe to csv file and add sequence and id lists
    df_good.insert(0, 'Sequence', seqs)
    df_good.insert(1, 'Ids', ids)
    df_good.to_csv(filename)
    filename = outputDir+'avgFluorTotalCounts.csv' # TODO: make into a config option
    df_total.insert(0, 'Sequence', seqs)
    df_total.insert(1, 'Ids', ids)
    df_total.to_csv(filename)
else:
    print('Counts reconstruction files exist. If want to rerun fluorescence reconstruction, delete: ', countFile)

filename = outputDir+'avgFluorGoodPercents.csv' # TODO: make into a config option
fileExists = check_file_empty(filename)
if fileExists == False:
    df_good, df_total = getReconstructedFluorescenceDf(numReplicates, dfBins, seqs, inputDir, outputDir, dfFlow, usePercents=True)
    # output dataframe to csv file and add sequence and id lists
    df_good.insert(0, 'Sequence', seqs)
    df_good.insert(1, 'Ids', ids)
    df_good.to_csv(filename)
    filename = outputDir+'avgFluorTotalPercents.csv' # TODO: make into a config option
    df_total.insert(0, 'Sequence', seqs)
    df_total.insert(1, 'Ids', ids)
    df_total.to_csv(filename)
else:
    print('Percent reconstruction files exist. If want to rerun fluorescence reconstruction, delete: ', filename)

filename = outputDir+'LBPercents.csv' # TODO: make into a config option
fileExists = check_file_empty(filename)
if fileExists == False:
    df_good, df_total = getReconstructedFluorescenceDf(numReplicates, dfBins, seqs, inputDir, outputDir, dfFlow, usePercents=True)
    # output dataframe to csv file and add sequence and id lists
    df_good.insert(0, 'Sequence', seqs)
    df_good.insert(1, 'Ids', ids)
    df_good.to_csv(filename)
    filename = outputDir+'avgFluorTotalPercents.csv' # TODO: make into a config option
    df_total.insert(0, 'Sequence', seqs)
    df_total.insert(1, 'Ids', ids)
    df_total.to_csv(filename)
else:
    print('Percent reconstruction files exist. If want to rerun fluorescence reconstruction, delete: ', filename)