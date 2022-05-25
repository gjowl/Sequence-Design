import sys
from functions import *
from ngsAnalysisFunctions import *

# MAIN
# Use the utilityFunctions function to get the name of this program
programName = getFilename(sys.argv[0])
configFile  = sys.argv[1]

# Read in configuration file:
globalConfig = read_config(configFile)
config = globalConfig[programName]

# Config file options:
countFile       = config["countFile"]
percentFile     = config["percentFile"]
flowFile        = config["flowFile"]
outputDir       = config["outputDir"]
inputDir        = config["inputDir"]
maltoseTestDir  = config["maltoseTestDir"]
countDir      = config["countDir"]
percentDir     = config["percentDir"]
reconstructionFile        = config["reconstructionFile"]

# control sequences
gpa = 'LIIFGVMAGVIGT'
g83i = 'LIIFGVMAIVIGL'

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

# filter out to only have the bins
dfBins = df.filter(like='C')

# get a dataframe for the file containing medians and percent population from flow csv
dfFlow = pd.read_csv(flowFile, index_col=0)

reconstructionDirList = [countDir, percentDir]
dfToReconstruct = [df, dfPercent]
usePercentOptionList = [False, True]
# reconstruct the fluorescence profile for the dataframe using both counts and percents (they give slightly different values)
# This outputs the dataframes into a list by method of calculating fluorescence: goodSeqs, totalSeqs, goodPercent, totalPercent
list_dfReconstructedFluor = reconstructFluorescenceForDfList(dfToReconstruct, reconstructionDirList, inputDir, dfFlow, seqs, segments, usePercentOptionList)

# hardcoded hour lists for LB and M9
LBhours = ['0H','12H','18H','30H']
M9hours = ['36H']
list_of_hours = [LBhours, M9hours]

# get the dataframes for LB and M9
dfLB = dfPercent.filter(like='LB')
dfM9 = dfPercent.filter(like='M9')
list_df = [dfLB, dfM9]
df_percentDiff = getPercentDifference(list_df, list_of_hours, seqs, segments, inputDir, maltoseTestDir)

# combine the percentDiff and fluorescence
list_dfFluorAndPercentDiff = [] 
percentDiffCol = df_percentDiff['18H']
for df in list_dfReconstructedFluor:
    df = df.assign(PercentDiff=percentDiffCol)
    list_dfFluorAndPercentDiff.append(df)

# for now, only going to output the df that uses total sequence percents (closest to SMA and JC data)
df_fluorAndPercent = list_dfFluorAndPercentDiff[3]
df_fluorAndPercent.to_csv(reconstructionFile)

# final step: separate out sequences that are above the cutoff into different dataframes
df_cutoff = df_fluorAndPercent[df_fluorAndPercent['PercentDiff'] > -95]
df_belowCutoff = df_fluorAndPercent[df_fluorAndPercent['PercentDiff'] < -95]
# get the avg fluorescence for sequences that are present in df_cutoff
aboveCutoffFile = outputDir +'aboveCutoff.csv'
belowCutoffFile = outputDir +'belowCutoff.csv'
df_cutoff.to_csv(aboveCutoffFile)
df_belowCutoff.to_csv(belowCutoffFile)
