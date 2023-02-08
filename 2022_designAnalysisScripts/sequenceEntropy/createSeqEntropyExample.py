import pandas as pd
import sys
import os
import random

# read in sequence entropy csv file
seqEntropy = pd.read_csv(sys.argv[1]) # 2021_12_05_seqEntropies.csv

# variables
numSeqsToGenerate = 100
seqLength = 8

outputDf = pd.DataFrame()
# generate sequences based on entropy
for i in range(numSeqsToGenerate):
    seq = ''
    for j in range(seqLength):
        # get random number between 0 and entropy max
        randNum = random.uniform(0, seqEntropy['Entropy'].max())
        # get a random AA from the entropy table that has an entropy value greater than the random number
        randAA = seqEntropy[seqEntropy['Entropy'] >= randNum].sample(1)['AA'].values[0]
        # add the random AA to the sequence
        seq += randAA
    # calculate the factorial for the seqLength
    numerator = 1
    for k in range(1, seqLength + 1):
        numerator *= k
    # get a list of unique AAs in the sequence
    uniqueAAs = list(set(seq))
    # calculate the number of permutations for the sequence
    denominator, entropy = 1, 1
    for aa in uniqueAAs:
        # get the number of times the unique AA appears in the sequence
        numAA = seq.count(aa)
        # bring the entropy of the aa to the power of the number of times it appears in the sequence
        aaEntropyContribution = seqEntropy[seqEntropy['AA'] == aa]['Entropy'].values[0] ** numAA
        entropy *= aaEntropyContribution
        # multiply the denominator by the factorial of the number of times the unique AA appears in the sequence
        for m in range(1, numAA + 1):
            denominator *= m
    # calculate the number of permutations for the sequence
    numPermutations = numerator / denominator
    # multiply the entropy by the number of permutations
    # this is the Shannon entropy for the sequence
    entropy *= numPermutations 
    # add the sequence to the df using concat
    print(seq, numerator, denominator, len(uniqueAAs), entropy)
    outputDf = pd.concat([outputDf, pd.DataFrame({'Sequence': [seq], 'Entropy': [entropy]})], ignore_index=True)

# get cwd
cwd = os.getcwd()
# write the output to a csv file
outputDf.to_csv(cwd+'/sequenceEntropyExample.csv', index=False)