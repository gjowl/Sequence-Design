import os, sys, pandas as pd
import matplotlib.pyplot as plt

def getWorstVoidMutants(df, numMutants=2):
    output_df = pd.DataFrame()
    for seq in df['Sequence'].unique():
        # loop through the sequences
        seq_df = df[df['Sequence'] == seq]
        # keep the sequences with the bottom 2 SasaDiff values
        seq_df = seq_df.nsmallest(numMutants, 'SasaPercDifference')
        # concat the directory_df to the top_void_df
        output_df = pd.concat([output_df, seq_df], axis=0)
    return output_df

if __name__ == '__main__':
    # get the command line arguments
    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # read in the csv file as a dataframe
    df = pd.read_csv(input_file, sep=',', header=0, dtype={'Interface': str})

    # change the amino acid at the position in the mutant to I
    df['Mutant'] = df.apply(lambda row: row['Mutant'][:row['Position']] + 'I' + row['Mutant'][row['Position']+1:], axis=1)
    # sort dataframe by region and sequence
    df = df.sort_values(by=['Region', 'Sequence'])
    # save the dataframe to a csv file
    df.to_csv(output_file, index=False)