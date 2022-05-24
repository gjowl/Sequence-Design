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
energyFile      = config["energyFile"]
outputDir       = config["outputDir"]
inputDir        = config["inputDir"]
maltoseTestDir  = config["maltoseTestDir"]
countDir      = config["countDir"]
percentDir     = config["percentDir"]

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

# hard coded defined number of replicates
numReplicates = 3
# get a dataframe for the file containing medians and percent population from flow csv
dfFlow = pd.read_csv(flowFile, index_col=0)

reconstructionDirList = [countDir, percentDir]
dfToReconstruct = [df, dfPercent]
usePercentOptionList = [False, True]
# reconstruct the fluorescence profile for the dataframe using both counts and percents (they give slightly different values)
# This outputs the dataframes into a list by method of calculating fluorescence: goodSeqs, totalSeqs, goodPercent, totalPercent
df_reconstructedFluorList = reconstructFluorescenceForDfList(dfToReconstruct, reconstructionDirList, inputDir, dfFlow, seqs, segments, numReplicates, usePercentOptionList)

for df in df_reconstructedFluorList:
    df = df[['Sequence','Average', 'StdDev']]

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

# I just realized: I may be losing sequences; some of the reading in the beginning that labels things unknown may be labeling it unknown if it just doesn't end in an L...
# Can I just remove that? Why is that there? actually nevermind, I think I'm okay, false alarm. It hsould only remove for DNA seqs, not for TM. and I fixed it so that it would 
# recognize my sequences buy removing an L? 
# Add LILI (end doesn't get read by NGS, but is present in the datafile of sequences that we're getting energies from
cutoffSeqs = df_cutoff['Sequence']+'LILI'
df_cutoffEnergyData = df_energyFile[df_energyFile['Sequence'].isin(cutoffSeqs)]

df_cutoffEnergyData = df_cutoffEnergyData.sort_values(by='Sequence')
df_cutoffEnergyData.reset_index(drop=True, inplace=True)
finalSeqs = df_cutoffEnergyData['Sequence']

df_finalOutputs = []
colsToAdd = ['Average', 'StdDev']

df = df_reconstructedFluorList[3] # this uses total seq count
# may have to change this: I think I should just use whatever the single g83i and gpa are from the flow (get those tomorrow or tonight and redo any analyses with those or just add them in)
g83iFluor = df.loc[df['Sequence'] == g83i, 'Average'].item()
# get g83i sequence
# do this for one sequence, make into a function, then for loop through it for the rest and figure out names later
df_out = df_cutoffEnergyData.copy()
# add in the LILI add the end of all sequences that doesn't get read by NGS but is found in the energy file of sequences
df['Sequence'] = df['Sequence']+'LILI'

df = df[df['Sequence'].isin(finalSeqs)]
df = df.sort_values(by='Sequence')
df.reset_index(drop=True, inplace=True)
for colName in df.columns:
    if colName in colsToAdd:
        df_out[colName] = pd.Series(df[colName])

# cutoff by g83i fluorescence
df_g83iCutoff = df_out[df_out['Average'] > g83iFluor]
print(df_g83iCutoff)
df_g83iCutoff.to_csv(outputDir+'seqsHigherThanG83i.csv')

# get just the designed sequences
df_designs = df_g83iCutoff[df_g83iCutoff['Sequence'] == df_g83iCutoff['StartSequence']]
print(df_designs)
df_designs.to_csv(outputDir+'designs.csv')
print('DONE!')

#for df in df_reconstructedFluorList:
#    df_out = df_cutoffEnergyData.copy()
#    # add in the LILI add the end of all sequences that doesn't get read by NGS but is found in the energy file of sequences
#    df['Sequence'] = df['Sequence']+'LILI'
#    df = df[df['Sequence'].isin(finalSeqs)]
#    df = df.sort_values(by='Sequence')
#    df.reset_index(drop=True, inplace=True)
#    for colName in df.columns:
#        if colName in colsToAdd:
#            df_out[colName] = pd.Series(df[colName])
#    df_finalOutputs.append(df_out)

#output_names = ['1.csv', '2.csv', '3.csv', '4.csv']
#for df, name in zip(df_finalOutputs, output_names):
#    print(df)
#    df.to_csv(outputDir+name)

# take all of the above, find G83I value, and rid of those as a G83I cutoff
# output 


#for seq in finalSeqs:
#    fluorAvgFinal = []
#    fluorStdDevFinal = []
#    for df in df_reconstructedFluorList:
#        fluorAvgFinal.append(df[df['Sequence' == seq]]['Average'])
#        fluorStdDevFinal.append(df[df['Sequence' == seq]]['StdDev'])
#    df_out = df_cutoffEnergyData.assign(fluorAvgFinal)
# next go through the sequences and add in columns of data for each sequence, and percent diff

#df_final = df_cutoffEnerggyData.assign(Fluorescence = col_fluor)
# need to read in the fluorescence file that I want to use
#df_cutoffEnergies.assign(Fluorescence = )
