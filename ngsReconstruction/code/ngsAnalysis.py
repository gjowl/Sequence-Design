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
countDir        = config["countDir"]
percentDir      = config["percentDir"]
reconstructionFile        = config["reconstructionFile"]

maltoseCutoff       = float(config["maltoseCutoff"])

# control sequences
gpa = 'LIIFGVMAGVIG'
g83i = 'LIIFGVMAIVIG'

# make the output directories that these will all output to
dirList = [outputDir, maltoseTestDir, countDir, percentDir]
for dir in dirList:
    makeOutputDir(dir)

# read csv containing counts
df = pd.read_csv(countFile, index_col=None)

# read csv containing percents
dfPercent = pd.read_csv(percentFile, index_col=None)

# get the first column (sequence column)
seqs = df.iloc[:,0]
segments = df.iloc[:,1]

# get a dataframe for the file containing medians and percent population from flow csv
# indices are the median and percent population values
dfFlow = pd.read_csv(flowFile, index_col=0)

reconstructionDirList = [countDir, percentDir]
dfToReconstruct = [df, dfPercent]
usePercentOptionList = [False, True]
# reconstruct the fluorescence profile for the dataframe using both counts and percents (they give slightly different values)
# This outputs the dataframes into a list by method of calculating fluorescence: goodSeqs, totalSeqs, goodPercent, totalPercent
list_dfReconstructedFluor = reconstructFluorescenceForDfList(dfToReconstruct, reconstructionDirList, inputDir, dfFlow, seqs, segments, usePercentOptionList)

# hardcoded hour lists for LB and M9
LBhours = ['0H','12H','24H','36H']
M9hours = ['24H', '36H']
list_of_hours = [LBhours, M9hours]

# get the dataframes for LB and M9
dfLB = dfPercent.filter(like='LB')
dfM9 = dfPercent.filter(like='M9')
list_df = [dfLB, dfM9]
df_percentDiff = getPercentDifference(list_df, list_of_hours, seqs, segments, inputDir, maltoseTestDir)

# combine the percentDiff and fluorescence
list_dfFluorAndPercentDiff = [] 
percentDiffCol = df_percentDiff['36H']
for df in list_dfReconstructedFluor:
    df = df.assign(MaltosePercentDiff=percentDiffCol)
    list_dfFluorAndPercentDiff.append(df)

# REORGANIZE THE COLUMNS OF THE DATAFRAME
# for now, only going to output the df that uses total sequence percents (closest to SMA and JC data)
df_fluorAndPercent = list_dfFluorAndPercentDiff[3]
# set the sequence column as the first column of the dataframe
seq_column = df_fluorAndPercent.pop('Sequence')
df_fluorAndPercent.insert(0, 'Sequence', seq_column)
# rename the average column to fluorescence and set it to the third column
fluor_column = df_fluorAndPercent.pop('Average')
df_fluorAndPercent.insert(2, 'Fluorescence', fluor_column)
# rename the stdDev column and set it to the fourth column
fluor_column = df_fluorAndPercent.pop('StdDev')
df_fluorAndPercent.insert(3, 'FluorStdDev', fluor_column)

# ADD IN PERCENT GPA ADN STANDARD DEVIATION
# extract the gpa and g83i fluorescence from the df_fluorAndPercent dataframe
gpaFluorescence = df_fluorAndPercent.loc[df_fluorAndPercent['Sequence'] == gpa, 'Fluorescence'].values[0]
g83IFluorescence = df_fluorAndPercent.loc[df_fluorAndPercent['Sequence'] == g83i, 'Fluorescence'].values[0]
print(gpaFluorescence)
print(g83IFluorescence)
gpaFluorescence = float(config["gpaFluor"])
g83IFluorescence = float(config["g83iFluor"])
# calculate percent GpA of fluorescence
percentGpaCol = df_fluorAndPercent['Fluorescence']/gpaFluorescence*100
percentGpaStdDevCol = df_fluorAndPercent['FluorStdDev']/gpaFluorescence*100
# add the percent GpA column to the dataframe
df_fluorAndPercent.insert(4, 'PercentGpa', percentGpaCol)
df_fluorAndPercent.insert(5, 'PercentGpaStdDev', percentGpaStdDevCol)

# WRITE THE DATAFRAMES TO A CSV
df_fluorAndPercent.to_csv(reconstructionFile, index=False)

# RID OF ANYTHING BELOW G83I FLUORESCENCE (MORE STABLE THAN MONOMER G83I)
df_aboveG83I = df_fluorAndPercent[df_fluorAndPercent['Fluorescence'] > g83IFluorescence]
g83iCutoffFile = outputDir + 'g83iCutoff.csv'
df_aboveG83I.to_csv(g83iCutoffFile, index=False)

# MALTOSE CUTOFF
df_cutoff = df_fluorAndPercent[df_fluorAndPercent['MaltosePercentDiff'] > maltoseCutoff]
df_belowCutoff = df_fluorAndPercent[df_fluorAndPercent['MaltosePercentDiff'] < maltoseCutoff]
aboveCutoffFile = outputDir +'aboveCutoff.csv'
belowCutoffFile = outputDir +'belowCutoff.csv'
df_cutoff.to_csv(aboveCutoffFile, index=False)
df_belowCutoff.to_csv(belowCutoffFile, index=False)