import os, sys, pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def getTopVoidMutants(df, numMutants=2):
    output_df = pd.DataFrame()
    for seq in df['Sequence'].unique():
        # loop through the sequences
        seq_df = df[df['Sequence'] == seq]
        # keep the sequences with the top 2 SasaDiff values
        seq_df = seq_df.nlargest(numMutants, 'SasaPercDifference')
        # concat the directory_df to the top_void_df
        output_df = pd.concat([output_df, seq_df], axis=0)
    return output_df

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

if __name__ == "__main__":
    # read in the command line arguments
    input_file = sys.argv[1]
    polyAla_file = sys.argv[2]
    output_file = sys.argv[3]
    output_dir = sys.argv[4]

    # read in the csv file as a dataframe
    mutant_df = pd.read_csv(input_file, sep=',', header=0, dtype={'Interface': 'str'})
    polyAla_df = pd.read_csv(polyAla_file, sep=',', header=None)
    # multiply the polyAla values by 2 to get the total sasa (currently loads up monomer sasa file)
    polyAla_df = polyAla_df * 2
    # rid of data where Sequence == mutant
    mutant_df = mutant_df[mutant_df['Sequence'] != mutant_df['Mutant']]

    # rename columns to make them more readable
    mutant_df.rename(columns={'Start': 'WT_Position_Sasa', 'Total_x': 'WT_Dimer_Sasa', 'TotalMutant': 'Mutant_Dimer_Sasa', 'Mutant.1': 'Mutant_Position_Sasa'}, inplace=True)
    # rename multiple columns
    mutant_df.rename(columns={'Total': 'Total_x', 'Total.1': 'TotalMutant'}, inplace=True)
    print(len(mutant_df))

    # Step one: check if the monomer sasa of each amino acid is increased
    mutant_df = mutant_df[mutant_df['WT_Position_Sasa'] < mutant_df['WT_Position_MonomerSasa']*2]
    print(len(mutant_df))

    # Step two: check if the sasa with alanine at that position leads to more sasa elsewhere
    # get the monomer without alanine sasa
    mutant_df['Mutant_SASA_no_alanine'] = mutant_df['Mutant_Dimer_Sasa'] - mutant_df['Mutant_Position_Sasa']
    # get the sasa without the wt position sasa
    mutant_df['SASA_no_wt_position'] = mutant_df['WT_Dimer_Sasa'] - mutant_df['WT_Position_Sasa']
    # keep the data where the mutant sasa is greater than the sequence sasa
    mutant_df = mutant_df[mutant_df['Mutant_SASA_no_alanine'] > mutant_df['SASA_no_wt_position']]
    print(len(mutant_df))

    # Step three: check if the sasa at the mutant position is exposed by comparing to polyAla
    
    # find positions in sequence that are not the same in the mutant
    mutant_df['Position'] = mutant_df.apply(lambda row: [i for i in range(len(row['Sequence'])) if row['Sequence'][i] != row['Mutant'][i]], axis=1)
    # convert the position column to an integer
    mutant_df['Position'] = mutant_df['Position'].apply(lambda x: int(x[0]))
    # get the AA in the sequence for the position
    mutant_df['WT_AA'] = mutant_df.apply(lambda row: row['Sequence'][row['Position']], axis=1)
    # initialize the SasaDifference list
    sasaDiff_list = []
    sasaPercDiff_list = []
    # loop through the mutants 
    for mutant in mutant_df['Mutant']:
        # get the position of the mutant
        position = mutant_df[mutant_df['Mutant'] == mutant]['Position'].values[0]
        # get the ith column of polyAla_df where i is the position of the mutant
        polyAla = polyAla_df.iloc[:, position].values[0]
        # get the mutant sasa
        mutant_sasa = mutant_df[mutant_df['Mutant'] == mutant]['Mutant_Position_Sasa'].values[0]
        # get the difference between the polyAla and the mutant sasa
        sasaDiff = polyAla - mutant_sasa
        # append the difference to the sasaDiff list
        sasaDiff_list.append(sasaDiff)
        # get the sasa percentage difference
        sasaPercDiff = (mutant_sasa / polyAla) * 100
        # append the sasa percentage difference to the sasaPercDiff list
        sasaPercDiff_list.append(sasaPercDiff)
    # add the sasaDiff and sasaPercDiff lists to the mutant_df
    mutant_df['SasaDifference'] = sasaDiff_list
    mutant_df['SasaPercDifference'] = sasaPercDiff_list
    
    # output the dataframe to a csv file
    mutant_df.to_csv(f'{output_dir}/{output_file}', index=False)

    # get the top 2 void mutants
    top_void_df = getTopVoidMutants(mutant_df)
    # output the dataframe to a csv file
    top_void_df.to_csv(f'{output_dir}/top_void_mutants.csv', index=False)

    # get the worst 2 void mutants
    worst_void_df = getWorstVoidMutants(mutant_df)
    # output the dataframe to a csv file
    worst_void_df.to_csv(f'{output_dir}/worst_void_mutants.csv', index=False)

    # make a boxplot of the SasaDifference for each position for each interface
    for interface in top_void_df['Interface'].unique():
        interface_df = top_void_df[top_void_df['Interface'] == interface]
        # plot the boxplot for each position
        sns.boxplot(x='Position', y='SasaPercDifference', data=interface_df)
        plt.xlabel('Position')
        plt.ylabel('Alanine SASA % Difference')
        plt.title(f'Interface: {interface}')
        # set the y axis to be from 0-100
        plt.ylim(0, 100)
        plt.savefig(f'{output_dir}/void_mutants_sasadiff_{interface}.png', dpi=500)
        plt.clf()

    # make a boxplot of the SasaDifference for each position for each interface
    for interface in worst_void_df['Interface'].unique():
        interface_df = worst_void_df[worst_void_df['Interface'] == interface]
        # plot the boxplot for each position
        sns.boxplot(x='Position', y='SasaPercDifference', data=interface_df)
        plt.xlabel('Position')
        plt.ylabel('Alanine SASA % Difference')
        plt.title(f'Interface: {interface}')
        # set the y axis to be from 0-100
        plt.ylim(0, 100)
        plt.savefig(f'{output_dir}/clash_mutants_sasadiff_{interface}.png', dpi=500)
        plt.clf()

