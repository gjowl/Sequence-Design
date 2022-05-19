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
percentFile     = config["percentFile"]
flowFile        = config["flowFile"]
outputDir       = config["outputDir"]
inputDir        = config["inputDir"]

# make the output directory that these will all output to
makeOutputDir(outputDir)

# read csv containing counts
df = pd.read_csv(countFile)
dfPercent = pd.read_csv(percentFile)

# filter out to only have the bins
# get the first column (sequence column)
seqs = df.iloc[:,0]
# filter for bins, LB, and M9
dfBins = df.filter(like='C')

# filter out to only have Rep1
numReplicates = 3
dfFlow = pd.read_csv(flowFile, index_col=0)
i=1

# if counts file exists, don't recreate
filename = outputDir+'avgFluorGoodCounts.csv' # TODO: make into a config option
fileExists = check_file_empty(filename)
if fileExists == False:
    df_good, df_total = getReconstructedFluorescenceDf(numReplicates, dfBins, seqs, inputDir, outputDir, dfFlow, usePercents=False)
    # output dataframe to csv file and add sequence id lists
    df_good.insert(0, 'Sequence', seqs)
    df_good.to_csv(filename)
    filename = outputDir+'avgFluorTotalCounts.csv' # TODO: make into a config option
    df_total.insert(0, 'Sequence', seqs)
    df_total.to_csv(filename)
else:
    print('Counts reconstruction files exist. If want to rerun fluorescence reconstruction, delete: ', countFile)

dfBins = dfPercent.filter(like='C')
filename = outputDir+'avgFluorGoodPercents.csv' # TODO: make into a config option
fileExists = check_file_empty(filename)
if fileExists == False:
    df_good, df_total = getReconstructedFluorescenceDf(numReplicates, dfBins, seqs, inputDir, outputDir, dfFlow, usePercents=True)
    # output dataframe to csv file and add sequence lists
    df_good.insert(0, 'Sequence', seqs)
    df_good.to_csv(filename)
    filename = outputDir+'avgFluorTotalPercents.csv' # TODO: make into a config option
    df_total.insert(0, 'Sequence', seqs)
    df_total.to_csv(filename)
else:
    print('Percent reconstruction files exist. If want to rerun fluorescence reconstruction, delete: ', filename)

#TODO: since I'm using the total above, maybe I should also calculate total percents? 
# filter main dataframe for LB
hours = ['0','12','18','30']
dfLB = dfPercent.filter(like='LB')
filename = outputDir+'LBPercents.csv' # TODO: make into a config option
fileExists = check_file_empty(filename)
if fileExists == False:
    df_LB = getPercentChange(numReplicates, hours, dfLB, seqs, inputDir, outputDir)
    # output dataframe to csv file and add sequence lists
    df_good.insert(0, 'Sequence', seqs)
    df_good.to_csv(filename)
else:
    print('Percent reconstruction files exist. If want to rerun fluorescence reconstruction, delete: ', filename)

hours = ['0']
dfM9 = dfPercent.filter(like='M9')
filename = outputDir+'M9Percents.csv' # TODO: make into a config option
fileExists = check_file_empty(filename)
if fileExists == False:
    df_M9 = getPercentChange(numReplicates, hours, dfM9, seqs, inputDir, outputDir)
    df_M9LBRatio = df_LB.div(df_M9.iloc[0])
    print(df_M9LBRatio)
    # output dataframe to csv file and add sequence lists
    df_M9.insert(0, 'Sequence', seqs)
    df_M9.to_csv(filename)
else:
    print('Percent reconstruction files exist. If want to rerun fluorescence reconstruction, delete: ', filename)