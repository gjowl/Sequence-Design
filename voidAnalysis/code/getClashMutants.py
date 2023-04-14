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
    mutant_file = sys.argv[1]
    interface_file = sys.argv[2]
    output_file = sys.argv[3]
    output_dir = sys.argv[4]

    # make the output directory if it doesn't exist
    os.makedirs(name=output_dir, exist_ok=True)

    # read in the csv file as a dataframe
    mutant_df = pd.read_csv(mutant_file, sep=',', header=0, dtype={'Interface': str})
    interface_df = pd.read_csv(interface_file, sep=',', header=0, dtype={'Interface': str})

    # only keep the data in the mutant_df where the sequence contains _
    mutant_df = mutant_df[mutant_df['Sequence'].str.contains('_')]

    # concat the interface_df to the mutant_df
    mutant_df = pd.concat([mutant_df, interface_df], axis=0)

    # output the data to a csv file
    mutant_df.to_csv(f'{output_dir}/{output_file}', sep=',', index=False)
    print(len(mutant_df))

    # get the top 2 void mutants
    df = getWorstVoidMutants(mutant_df)
    # keep only unique mutants
    df = df.drop_duplicates(subset=['Mutant'], keep='first')
    # output the data to a csv file
    df.to_csv(f'{output_dir}/{output_file}_worst_void.csv', sep=',', index=False)

    # find positions in sequence that are not the same in the mutant
    df['Position'] = df.apply(lambda row: [i for i in range(len(row['Sequence'])) if row['Sequence'][i] != row['Mutant'][i]], axis=1)
    # change the amino acid at the position in the mutant to I
    df['Mutant'] = df.apply(lambda row: row['Mutant'][:row['Position']] + 'I' + row['Mutant'][row['Position']+1:], axis=1)
    # sort dataframe by region and sequence
    df = df.sort_values(by=['Region', 'Sequence'])
    # save the dataframe to a csv file
    df.to_csv(output_file, index=False)