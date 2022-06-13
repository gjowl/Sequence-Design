import sys
from functions import *

def addColumnsToFrontOfDf(df, colNames):
    df_output = df.copy()
    for colName in colNames:
        col = df_output.pop(colName)
        df_output.insert(0, colName, col)
    return df_output
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

# variables
fluorCol = 'Fluorescence'
stdDevCol = 'FluorStdDev'
percentGpaCol = 'PercentGpa'
percentGpaStdDevCol = 'PercentGpaStdDev'
maltoseCol = 'MaltosePercentDiff'
colsToAdd = [fluorCol, stdDevCol, percentGpaCol, percentGpaStdDevCol, maltoseCol]

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

# I found an issue with this: my energy file sometimes has duplicate sequences:
# mutants to some sequences end up being the same as a starting sequence
# So instead of just adding columns, I'll need to add info for each sequence
# add the fluorescence, stdDev, and percent difference to the energy dataframe
for colName in df_fluor.columns:
    if colName in colsToAdd:
        list_values = [] 
        for seq in df_energyAndFluor['Sequence']:
            # get the sequence info for the given column
            value = df_fluorFiltered.loc[df_fluorFiltered['Sequence'] == seq, colName].item()
            list_values.append(value)
        df_energyAndFluor = insertAtEndOfDf(df_energyAndFluor, colName, list_values)

# reverse columns to add them to the front of the dataframe in proper order
colsToAdd.reverse()
df_output = addColumnsToFrontOfDf(df_energyAndFluor, colsToAdd)

# rename energy column Total -> EnergyScore and add to front of dataframe
energyScore = df_output.pop('Total')
df_output.insert(0, 'EnergyScore', energyScore)
# add sequence column to front of dataframe
sequence = df_output.pop('Sequence')
df_output.insert(0, 'Sequence', sequence)

# output the dataframe
allDatafile = outputDir+'allData.csv'
df_output.to_csv(allDatafile, index=False)

# get just design sequences
df_designs = df_energyAndFluor[df_energyAndFluor['Sequence'].isin(df_energyAndFluor['StartSequence'])]
designDatafile = outputDir+'designData.csv'
df_designs.to_csv(designDatafile, index=False)

# get only clashing sequences
df_clash = df_energyAndFluor[df_energyAndFluor['Total'] > 0]
exit()
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

# get just the designed sequences
df_designs = df[df['Sequence'] == df['StartSequence']]
df_designs.to_csv(outputDir+'designs.csv')
print('DONE!')

# uncomment and change below if planning to run alphafold on these designs
# TODO: write a bit of code that will take the sequence and write out fasta and colabfold files for them
# write colabfold csv file
#colabfoldFile = outputDir+'colabfold_clashing.csv'
#df_colab = pd.DataFrame()
#seqColumn = df_clash['Sequence']
#fastaColumn = df_clash['Sequence']+'.fasta'
#df_colab = insertAtEndOfDf(df_colab, 'fasta', fastaColumn)
#df_colab = insertAtEndOfDf(df_colab, 'Sequence', seqColumn)

# write fasta files for all sequences
#fastaDir = '/mnt/d/fasta/'
#for seq, fasta in zip(df_colab['Sequence'], df_colab['fasta']):
#    filename = fastaDir+fasta
#    with open(filename, 'w') as f:
#        f.write('>'+seq+'\n')
#        f.write(seq+':'+seq)
#    f.close()
#
#df_colab = df_colab.set_index('fasta')
#df_colab.to_csv(colabfoldFile, header=False, index=False)
