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
    
    # get the name of the input file without the file extension
    input_filename = os.path.splitext(os.path.basename(input_file))[0]

    # define the amino acids to mutate to
    amino_acids = ['I', 'L', 'A', 'F']

    # read in the input file as a dataframe
    df = pd.read_csv(input_file)
    # only keep one copy of each sequence
    df = df.drop_duplicates(subset=['Sequence'], keep='first')

    # initialize the output dataframe
    output_df = pd.DataFrame()
    # loop through each sequence in the dataframe
    for sequence in df['Sequence'].unique():
        # loop through the positions to mutate
        for position in positions_to_mutate:
            # loop through the amino acids to mutate to
            successful_mutations = 0
            mutant_sequence_df = pd.DataFrame()
            for amino_acid in amino_acids:
                # check if the number of successful mutations is greater than 2
                if len(mutant_sequence_df) > 0:
                    # if so, break out of the loop and go to the next sequence/position
                    break
                # check if the amino acid is the same as the wild type
                if amino_acid == sequence[position]:
                    # if so, skip this iteration
                    continue
                # mutate the sequence at the position
                mutant_sequence = mutateSequence(sequence, position, amino_acid)
                # add the mutant sequence to the dataframe using concat
                mutant_sequence_df = pd.concat([mutant_sequence_df, pd.Series(mutant_sequence)], axis=0)
            # add the mutant sequence dataframe to the output dataframe
            output_df = pd.concat([output_df, mutant_sequence_df], axis=0)
    
    # reset the index of the output dataframe
    output_df = output_df.reset_index(drop=True)
    # save the output dataframe to a csv file
    output_df.to_csv(f'{output_dir}/{input_filename}_mutants.csv', index=False)
    
