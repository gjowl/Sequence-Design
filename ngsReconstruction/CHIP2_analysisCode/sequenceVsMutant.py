
import sys, os, pandas as pd, numpy as np, matplotlib.pyplot as plt

def match(s1, s2):
    num_diff = 0
    for i, (c1, c2) in enumerate(zip(s1, s2)):
        if c1 != c2:
            num_diff += 1
    return num_diff 

# read in the input files
sequenceFile = sys.argv[1]
mutantFile = sys.argv[2]

# read in the dataframes
df_sequence = pd.read_csv(sequenceFile)
df_mutant = pd.read_csv(mutantFile)

samples = df_sequence['Sample'].unique()
for sample in samples:
    df_sample = df_sequence[df_sequence['Sample'] == sample]
    df_sample_mutant = df_mutant[df_mutant['Sample'] == sample]
    # loop through all of the sequences
    for seq in df_sample['Sequence'].unique():
        matching_sequences = [seq]
        for seq2  in df_sample['Sequence'].unique():
            if match(seq, seq2) < 2:
                matching_sequences.append(seq2)
        for mut in df_sample_mutant['Mutant'].unique():
            if match(seq, mut) < 2:
                matching_sequences.append(mut)
        # keep only the unique sequences
        matching_sequences = list(set(matching_sequences))
        print(matching_sequences)
        # think of a way to keep the mutants that also don't fluoresce here? Maybe if I just label each sequence as a mutant or not?
        # also, should I keep the maltose cutoff too? that way, if something with like a G83i like mutation is gone, that can be the justification?
        exit(0)
