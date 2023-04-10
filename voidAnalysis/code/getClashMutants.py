import os, sys, pandas as pd
import matplotlib.pyplot as plt

def getWorstVoidMutants(df, numMutants=2):
    output_df = pd.DataFrame()
    for seq in df['Sequence'].unique():
        # loop through the sequences
        seq_df = df[df['Sequence'] == seq]
        # keep the sequences with the bottom 2 SasaDiff values
        seq_df = seq_df.nsmallest(numMutants, 'SasaDifference')
        # concat the directory_df to the top_void_df
        output_df = pd.concat([output_df, seq_df], axis=0)
    return output_df

if __name__ == '__main__':
    # get the command line arguments
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    output_dir = sys.argv[3]

    # read in the csv file as a dataframe
    df = pd.read_csv(input_file, sep=',', header=0, dtype={'Interface': str})
    # get the top 2 void mutants
    df = getWorstVoidMutants(df)
    # keep only unique mutants
    df = df.drop_duplicates(subset=['Mutant'], keep='first')

    # find positions in sequence that are not the same in the mutant
    df['Position'] = df.apply(lambda row: [i for i in range(len(row['Sequence'])) if row['Sequence'][i] != row['Mutant'][i]], axis=1)
    # change the amino acid at the position in the mutant to I
    df['Mutant'] = df.apply(lambda row: row['Mutant'][:row['Position'][0]] + 'I' + row['Mutant'][row['Position'][0]+1:], axis=1)
    # remove the position column
    df = df.drop(columns=['Position'])
    # sort dataframe by region and sequence
    df = df.sort_values(by=['Region', 'Sequence'])
    # save the dataframe to a csv file
    df.to_csv(output_file, index=False)
    
    # create a boxplot of the SasaDifference
    plt.figure()

    # color the scatter plot differently for each region
    for region in df['Region'].unique():
        # get the data for the region
        region_df = df[df['Region'] == region]
        # plot the data
        plt.scatter(region_df['Total'], region_df['SasaDifference'], label=region)
    plt.title('SasaDifference')
    # add a legend with the region names
    plt.legend()
    plt.xlabel('Total Energy')
    plt.ylabel('SasaDifference')

    # save the figure
    plt.savefig(f'{input_file[:-4]}_bottom2.png', dpi=300)
            