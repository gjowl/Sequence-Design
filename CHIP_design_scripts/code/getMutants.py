import os, sys, pandas as pd

def mutateSequence(sequence, position, replacement):
    # mutate the sequence
    mutant_sequence = sequence[:position] + replacement + sequence[position + 1:]
    return mutant_sequence


if __name__ == '__main__':
    # read in the command line arguments
    input_file = sys.argv[1]
    output_dir = sys.argv[2]
    positions_to_mutate = [int (i) for i in sys.argv[3:]]

    # define the amino acids to mutate to
    amino_acids = ['A', 'I', 'F', 'W']

    # read in the input file as a dataframe
    df = pd.read_csv(input_file)
    mutant_sequence_df = df['Sequence'].copy()

    # initialize the output dataframe
    output_df = pd.DataFrame()
    # loop through each sequence in the dataframe
    for sequence in df['Sequence'].unique():
        # loop through the positions to mutate
        for position in positions_to_mutate:
            # loop through the amino acids to mutate to
            for amino_acid in amino_acids:
                # mutate the sequence at the position
                mutant_sequence = mutateSequence(sequence, position)
                # add the mutant sequence to the dataframe using concat
                output_df = output_df.append({'Sequence': mutant_sequence}, ignore_index=True)
