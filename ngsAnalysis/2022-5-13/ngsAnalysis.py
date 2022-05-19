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
segments = df.iloc[:,1]
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
    df_good.insert(1, 'Segments', segments)
    df_good.to_csv(filename)
    filename = outputDir+'avgFluorTotalCounts.csv' # TODO: make into a config option
    df_total.insert(0, 'Sequence', seqs)
    df_total.insert(1, 'Segments', segments)
    df_total.to_csv(filename)
else:
    print('Counts reconstruction files exist. If want to rerun fluorescence reconstruction, delete: ', countFile)

#TODO: I think I can make this into a function that just runs through a list of dataframes?
dfBins = dfPercent.filter(like='C')
# initialize good and total percent dataframes
df_good = pd.DataFrame()
df_total = pd.DataFrame()
filename = outputDir+'avgFluorGoodPercents.csv' # TODO: make into a config option
fileExists = check_file_empty(filename)
if fileExists == False:
    df_good, df_total = getReconstructedFluorescenceDf(numReplicates, dfBins, seqs, inputDir, outputDir, dfFlow, usePercents=True)
    # output dataframe to csv file and add sequence lists
    #TODO: make into a functions below adding these parts in
    df_good.insert(0, 'Sequence', seqs)
    df_good.insert(1, 'Segments', segments)
    df_good = df_good.set_index('Sequence')
    df_good.to_csv(filename)
    filename = outputDir+'avgFluorTotalPercents.csv' # TODO: make into a config option
    df_total.insert(0, 'Sequence', seqs)
    df_total.insert(1, 'Segments', segments)
    df_total = df_total.set_index('Sequence')
    df_total.to_csv(filename)
else:
    print('Percent reconstruction files exist. If want to rerun fluorescence reconstruction, delete: ', filename)

#TODO: since I'm using the total above, maybe I should also calculate total percents? 
# filter main dataframe for LB
hours = ['0H','12H','18H','30H']
# TODO: I think I can automate this by just taking from the names?
dfLB = dfPercent.filter(like='LB')
dfM9 = dfPercent.filter(like='M9')
LBFile = outputDir+'LBPercents.csv' # TODO: make into a config option
M9File = outputDir+'M9Percents.csv' # TODO: make into a config option
percentFile = outputDir+'percentsDifference.csv' # TODO: make into a config option
LBFileExists = check_file_empty(LBFile)
M9FileExists = check_file_empty(M9File)
# initialize percent difference dataframe
df_percentDiff = pd.DataFrame()
if LBFileExists == False or M9FileExists == False:
    df_LB = getMeanPercent(numReplicates, hours, dfLB, inputDir, outputDir)
    # output dataframe to csv file and add sequence lists
    hours = ['36H']
    df_M9 = getMeanPercent(numReplicates, hours, dfM9, inputDir, outputDir)
    # output dataframe to csv file and add sequence lists
    df_percentDiff = calculatePercentDifference(df_LB, df_M9)
    df_percentDiff.insert(0, 'Sequence', seqs)
    df_percentDiff.insert(1, 'Segments', segments)
    df_percentDiff = df_percentDiff.set_index('Sequence')
    df_LB.insert(0, 'Sequence', seqs)
    df_M9.insert(0, 'Sequence', seqs)
    df_LB.to_csv(LBFile)
    #df_M9.to_csv(M9File)
    df_percentDiff.to_csv(percentFile)
else:
    print('Percent reconstruction files exist. If want to rerun fluorescence reconstruction, delete: ', filename)

# final step: separate out sequences that are above the cutoff into different dataframes
# TODO: get a cutoff for the 18H neg  control with the lowest value
df_cutoff = df_percentDiff[df_percentDiff['18H'] > -95]
df_belowCutoff = df_percentDiff[df_percentDiff['18H'] < -95]
print(df_cutoff)
# get the avg fluorescence for sequences that are present in df_cutoff
aboveCutoffFile = outputDir +'aboveCutoff.csv'
belowCutoffFile = outputDir +'belowCutoff.csv'
df_cutoff.to_csv(aboveCutoffFile)
df_belowCutoff.to_csv(belowCutoffFile)
# for Samson: send him all of the things with the segment name; maybe send him the sequence list