import os, sys, pandas as pd, matplotlib.pyplot as plt, numpy as np, argparse

# initialize the parser
parser = argparse.ArgumentParser(description='Calculated the single AA and multiple AA composition of a sequence file')
parser.add_argument('-seqFile','--sequenceFile', type=str, help='the input file of sequences to be analyzed')
# optional arguments
parser.add_argument('-outputDir','--outputDir', type=str, help='the output directory')

# extract the arguments into variables
args = parser.parse_args()
sequenceFile = args.sequenceFile
outputDir = 'AAComposition'
if args.outputDir is None:
    outputDir = args.outputDir
outputDir = args.outputDir
os.makedirs(outputDir, exist_ok=True)

if __name__ == "__main__":
    # read in the data file (extracted data from the pdb files)
    sequence_df = pd.read_csv(sequenceFile)

    # combine all sequences into a single df
    allSequences = pd.DataFrame()
    allSequences['Sequence'] = sequence_df['Sequence 1']
    pd.concat([allSequences, sequence_df['Sequence 2']], ignore_index=True)

    # count the number of each amino acid in all sequences
    aaCounts = {}
    for seq in allSequences['Sequence']:
        for aa in seq:
            if aa in aaCounts:
                aaCounts[aa] += 1
            else:
                aaCounts[aa] = 1
    # convert the counts to a dataframe
    aaCounts_df = pd.DataFrame.from_dict(aaCounts, orient='index', columns=['Count'])
    aaCounts_df.index.name = 'Amino Acid'

    # remove the non-standard amino acids
    aaCounts_df = aaCounts_df.drop(['X'], errors='ignore')
    # calculate the percentage of each amino acid
    aaCounts_df['Percentage'] = aaCounts_df['Count'] / aaCounts_df['Count'].sum() * 100
    aaCounts_df.to_csv(f'{outputDir}/aaCounts.csv')

    # count the number of each pair of amino acids in all sequences
    aaPairs = {}
    for seq in allSequences['Sequence']:
        for i in range(len(seq)-1):
            pair = seq[i:i+2]
            if pair in aaPairs:
                aaPairs[pair] += 1
            else:
                aaPairs[pair] = 1
    # remove any pairs containing X
    aaPairs = {k: v for k, v in aaPairs.items() if 'X' not in k}

    # convert the counts to a dataframe
    aaPairs_df = pd.DataFrame.from_dict(aaPairs, orient='index', columns=['Count'])
    aaPairs_df.index.name = 'Amino Acid Pair'
    # calculate the percentage of each amino acid
    aaPairs_df['Percentage'] = aaPairs_df['Count'] / aaPairs_df['Count'].sum() * 100
    #aaPairs_df['Percentage'] = aaPairs_df['Count'] / len(allSequences) * 100
    # sort by the percentage of the pair
    aaPairs_df = aaPairs_df.sort_values(by='Percentage', ascending=False)
    aaPairs_df.to_csv(f'{outputDir}/aaPairs.csv')

    # find the number of unique sequences that have each pair of amino acids
    aaPairSeqs = {}
    for pair in aaPairs:
       aaPairSeqs[pair] = len(allSequences[allSequences['Sequence'].str.contains(pair)])
    # convert the counts to a dataframe
    aaPairsSeqs_df = pd.DataFrame.from_dict(aaPairs, orient='index', columns=['Count']) 
    aaPairsSeqs_df.index.name = 'Amino Acid Pair'
    aaPairsSeqs_df['Unique Sequences'] = aaPairsSeqs_df.index.map(aaPairSeqs)
    # calculate the pairs that occur most often in a single sequence
    aaPairsSeqs_df['Percentage'] = aaPairsSeqs_df['Count'] / aaPairsSeqs_df['Unique Sequences'] * 100
    # sort by the percentage of the pair in a single sequence
    aaPairsSeqs_df = aaPairsSeqs_df.sort_values(by='Percentage', ascending=False)
    aaPairsSeqs_df.to_csv(f'{outputDir}/aaPairsSeqs.csv')