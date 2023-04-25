import sys, os, pandas as pd

# get the output directory from the command line
outputDir = sys.argv[1]
dataFile = sys.argv[2]

# make the output directory if it doesn't exist
os.makedirs(outputDir, exist_ok=True)

# open the data file with interface as string
data = pd.read_csv(dataFile, dtype={'Interface':str})

# keep the sequence and interface column
sequences = data[['Sequence', 'Interface']]

# rename the sequences column to 'StartSequence'
sequences = sequences.rename(columns={'Sequence':'StartSequence'})

# make a new dataframe with the sequences column
outputDf = pd.DataFrame()

# mutation amino acids
mutateAas = ['F', 'A', 'W','P']
numberMutations = 3

# loop through the sequences and interfaces
for index, row in sequences.iterrows():
    # get the sequence and interface
    sequence = row['StartSequence']
    interface = row['Interface']
    # loop through the interface
    for i in range(len(interface)):
        # if the interface is 1, mutate the sequence
        if interface[i] == '1':
            # get the amino acid at the position
            aa = sequence[i]
            # set the number of mutations to 0
            numMutations = 0
            # loop through the mutateAas
            for mutateAa in mutateAas:
                # check if the amino acid is in the mutateAas list and if the number of mutations is less than the desired number
                if aa not in mutateAas and numMutations < numberMutations:
                    # mutate the sequence
                    newSequence = sequence[:i] + mutateAa + sequence[i+1:]
                    numMutations += 1
                    # add the new sequence to the output dataframe using concat
                    outputDf = pd.concat([outputDf, pd.DataFrame({'StartSequence':[sequence], 'MutantSequence':[newSequence], 'Interface':[interface]})])
# write the output dataframe to a csv file
outputDf.to_csv(outputDir + '/mutatedSequences.csv', index=False) 