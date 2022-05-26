
import sys
from functions import *

# MAIN
# Use the utilityFunctions function to get the name of this program
programName = getFilename(sys.argv[0])
configFile  = sys.argv[1]

# Read in configuration file:
globalConfig = read_config(configFile)
config = globalConfig[programName]

# Config file options:
outputDir          = config["outputDir"]
energyFile         = config["energyFile"]
reconstructionFile = config["reconstructionFile"]

# control sequences
gpa = 'LIIFGVMAGVIGT'
g83i = 'LIIFGVMAIVIGL'

# make the output directories that these will all output to
dirList = [outputDir]
for dir in dirList:
    makeOutputDir(dir)

# read in the input files
df_energyFile = pd.read_csv(energyFile)
df_fluor = pd.read_csv(reconstructionFile)

# initialize a new dataframe that will be used for analysis and output
df_output = pd.DataFrame()

# find the sequences from the energy file that are present in the reconstruction file
#   - first get a sequence list: sequences in energyFile have added LILI, so add here
seqs = df_fluor['Sequence']+'LILI'
df_fluor['Sequence'] = seqs
df_energyAndFluor = df_energyFile[df_energyFile['Sequence'].isin(seqs)]
df_energyAndFluor = df_energyAndFluor.sort_values(by='Sequence')
df_energyAndFluor.reset_index(drop=True, inplace=True)
finalSeqs = df_energyAndFluor['Sequence']

# remove the sequences that aren't present in the energy file
df_fluorFiltered = df_fluor[df_fluor['Sequence'].isin(finalSeqs)]
df_fluorFiltered = df_fluorFiltered.sort_values(by='Sequence')
df_fluorFiltered.reset_index(drop=True, inplace=True)

# add the fluorescence, stdDev, and percent difference to the energy dataframe
colsToAdd = ['Average', 'StdDev', 'PercentDiff']
for colName in df_fluor.columns:
    if colName in colsToAdd:
        df_energyAndFluor[colName] = pd.Series(df_fluorFiltered[colName])

# output the dataframe
allDatafile = outputDir+'allData.csv'
df_energyAndFluor.to_csv(allDatafile)

exit()

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