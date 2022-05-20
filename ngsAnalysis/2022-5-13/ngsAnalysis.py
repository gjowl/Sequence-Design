import sys
import helper
from functions import *
from ngsAnalysisFunctions import *


# main function for fluorescence reconstruction
def reconstructFluorescenceForDfList(dfToReconstruct, reconstructionDirList, inputDir, dfFlow, seqs, segments, numReplicates, usePercentOptionList):
    # loop through the lists of reconstruction dfs, dirs, and percent options (these should all be the same length)
    for df, outputDir, usePercent in zip(dfToReconstruct, reconstructionDirList, usePercentOptionList):
        # if the dir is empty, continue
        if len(os.listdir(outputDir)) < 20:
            dfBins = df.filter(like='C')
            # reconstruct the fluorescence for both good and total sequence numbers
            df_good, df_total = getReconstructedFluorescenceDf(numReplicates, dfBins, seqs, segments, inputDir, outputDir, dfFlow, usePercent)
            outputAnalysisDfToCsv(df_good, seqs, segments, outputDir, 'avgFluorGoodSeqs.csv') 
            outputAnalysisDfToCsv(df_total, seqs, segments, outputDir, 'avgFlourTotalSeqs.csv') 
        else:
            print(outputDir, "files already made. If want to remake, make sure the directory is empty")

# main function for getting the percent difference between LB and M9 for maltose test
def getPercentDifference(list_df, list_of_hours, numReplicates, seqs, segments, inputDir, outputDir):
    df_percentDiff = pd.DataFrame()
    if len(os.listdir(outputDir)) == 0:
        # list to hold the output df: the first output is for LB and the second is for M9
        # after the loop, it uses both to calculate the percent difference 
        outputDfs = []
        for df, hourList in zip(list_df, list_of_hours):
            outputDf = getMeanPercent(numReplicates, hourList, df, inputDir, outputDir)
            outputDfs.append(outputDf)
        df_percentDiff = calculatePercentDifference(outputDfs[0], outputDfs[1])
        outputDfs.append(df_percentDiff)
        nameList = ['LBPercents.csv', 'M9Percents.csv', 'percentDifference.csv']
        for df, name in zip(outputDfs, nameList):
            outputAnalysisDfToCsv(df, seqs, segments, outputDir, name)
    else:
        print('Percent difference file exists, loading it into dataframe...')
        df_percentDiff = pd.read_csv(outputDir+'percentDifference.csv')
        print('dataframe loaded; If want to remake fluorescence difference file, delete all files in: ', outputDir)
    return df_percentDiff
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
energyFile      = config["energyFile"]
outputDir       = config["outputDir"]
inputDir        = config["inputDir"]
maltoseTestDir  = config["maltoseTestDir"]
countDir      = config["countDir"]
percentDir     = config["percentDir"]

# make the output directories that these will all output to
dirList = [outputDir, maltoseTestDir, countDir, percentDir]
for dir in dirList:
    makeOutputDir(dir)

# read csv containing counts
df = pd.read_csv(countFile)
# read csv containing percents
dfPercent = pd.read_csv(percentFile)
# get the first column (sequence column)
seqs = df.iloc[:,0]
segments = df.iloc[:,1]
# filter for bins, LB, and M9
# filter out to only have the bins
dfBins = df.filter(like='C')

# hard coded defined number of replicates
numReplicates = 3
# get a dataframe for the file containing medians and percent population from flow csv
dfFlow = pd.read_csv(flowFile, index_col=0)

reconstructionDirList = [countDir, percentDir]
dfToReconstruct = [df, dfPercent]
usePercentOptionList = [False, True]
# reconstruct the fluorescence profile for the dataframe using both counts and percents (they give slightly different values)
reconstructFluorescenceForDfList(dfToReconstruct, reconstructionDirList, inputDir, dfFlow, seqs, segments, numReplicates, usePercentOptionList)

# hardcoded hour lists for LB and M9
LBhours = ['0H','12H','18H','30H']
M9hours = ['36H']
list_of_hours = [LBhours, M9hours]

# get the dataframes for LB and M9
dfLB = dfPercent.filter(like='LB')
dfM9 = dfPercent.filter(like='M9')
list_df = [dfLB, dfM9]
df_percentDiff = getPercentDifference(list_df, list_of_hours, numReplicates, seqs, segments, inputDir, maltoseTestDir)

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

# read in the energy file and only keep things that match sequence
df_energyFile = pd.read_csv(energyFile)
print(df_energyFile)

cutoffSeqs = df_cutoff['Sequence']
print(cutoffSeqs)
df_cutoffEnergies = df_energyFile[df_energyFile['Sequence'] == cutoffSeqs]
print(df_cutoffEnergies)
exit()
# need to read in the fluorescence file that I want to use
#df_cutoffEnergies.assign(Fluorescence = )


# for Samson: send him all of the things with the segment name; maybe send him the sequence list