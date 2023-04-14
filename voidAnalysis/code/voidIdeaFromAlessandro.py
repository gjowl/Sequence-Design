import os, sys, pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def getTopVoidMutants(df, numMutants=2):
    output_df = pd.DataFrame()
    for seq in df['Sequence'].unique():
        # loop through the sequences
        seq_df = df[df['Sequence'] == seq]
        # keep the sequences with the top 2 SasaDiff values
        seq_df = seq_df.nlargest(numMutants, 'DimerSasaDifference')
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

def getSasaPercentageDifference(mutant_df, polyAla_df):
    output_df = mutant_df.copy()
    # initialize the SasaDifference list
    sasaDiff_list = []
    sasaPercDiff_list = []
    # loop through the mutants 
    for mutant in output_df['Mutant']:
        # get the position of the mutant
        position = output_df[output_df['Mutant'] == mutant]['Position'].values[0]
        # get the ith column of polyAla_df where i is the position of the mutant
        polyAla = polyAla_df.iloc[:, position].values[0]
        # get the mutant sasa
        mutant_sasa = output_df[output_df['Mutant'] == mutant]['Mutant_Position_Sasa'].values[0]
        # get the difference between the polyAla and the mutant sasa
        sasaDiff = polyAla - mutant_sasa
        # append the difference to the sasaDiff list
        sasaDiff_list.append(sasaDiff)
        # get the sasa percentage difference
        sasaPercDiff = (mutant_sasa / polyAla) * 100
        # append the sasa percentage difference to the sasaPercDiff list
        sasaPercDiff_list.append(sasaPercDiff)
    # add the sasaDiff and sasaPercDiff lists to the output_df
    output_df['SasaDifference'] = sasaDiff_list
    output_df['SasaPercDifference'] = sasaPercDiff_list
    return output_df

if __name__ == "__main__":
    # read in the command line arguments
    input_file = sys.argv[1]
    polyAla_file = sys.argv[2]
    output_file = sys.argv[3]
    output_dir = sys.argv[4]

    # read in the csv file as a dataframe
    start_mutant_df = pd.read_csv(input_file, sep=',', header=0, dtype={'Interface': str})
    polyAla_df = pd.read_csv(polyAla_file, sep=',', header=None)
    # multiply the polyAla values by 2 to get the total sasa (currently loads up monomer sasa file)
    polyAla_df = polyAla_df * 2
    
    # add the sequences that have _ to another dataframe
    df_wt_data = start_mutant_df[start_mutant_df['Mutant'].str.contains('_')]
    # split by the _ and set the mutant to the first part of the split and the position to the second part of the split
    df_wt_data[['Mutant', 'Position']] = df_wt_data['Mutant'].str.split('_', expand=True)
    # set the Position column to an integer
    df_wt_data['Position'] = df_wt_data['Position'].apply(lambda x: int(x))
    # get the AA in the sequence for the position
    df_wt_data['WT_AA'] = df_wt_data.apply(lambda row: row['Sequence'][row['Position']], axis=1)

    # find positions in sequence that are not the same in the mutant
    start_mutant_df['Position'] = start_mutant_df.apply(lambda row: [i for i in range(len(row['Sequence'])) if row['Sequence'][i] != row['Mutant'][i]], axis=1)
    # check if position is empty
    start_mutant_df = start_mutant_df[start_mutant_df['Position'].apply(lambda x: len(x) > 0)]
    # convert the position column to an integer
    start_mutant_df['Position'] = start_mutant_df['Position'].apply(lambda x: int(x[0]))
    # get the AA in the sequence for the position
    start_mutant_df['WT_AA'] = start_mutant_df.apply(lambda row: row['Sequence'][row['Position']], axis=1)
    # concat the start mutant df with the df wt data
    start_mutant_df = pd.concat([start_mutant_df, df_wt_data], axis=0)
    # remove data where the Position is < 3 or > 17
    start_mutant_df = start_mutant_df[(start_mutant_df['Position'] > 2) & (start_mutant_df['Position'] < 18)]

    
    # get the sasa percentage difference
    start_mutant_df = getSasaPercentageDifference(start_mutant_df, polyAla_df)
    # output the start_mutant_df
    start_mutant_df.to_csv(f'{output_dir}/start_mutant_df.csv', index=False)

    # add the sequences that have _ to another dataframe
    df_wt_data = start_mutant_df[start_mutant_df['Mutant'].str.contains('_')]

    # rid of data where Sequence == mutant
    mutant_df = start_mutant_df[start_mutant_df['Sequence'] != start_mutant_df['Mutant']]

    # Step one: check if the monomer sasa of each amino acid is increased
    mutant_df = mutant_df[mutant_df['WT_Position_Sasa'] < mutant_df['WT_Position_MonomerSasa']*2]
    print(len(mutant_df))

    # Step two: check if the sasa with alanine at that position leads to more sasa elsewhere
    # get the monomer without alanine sasa
    mutant_df['Mutant_SASA_no_alanine'] = mutant_df['Mutant_DimerSasa'] - mutant_df['Mutant_Position_Sasa']
    # get the sasa without the wt position sasa
    mutant_df['SASA_no_wt_position'] = mutant_df['WT_DimerSasa'] - mutant_df['WT_Position_Sasa']
    # keep the data where the mutant sasa is greater than the sequence sasa
    mutant_df = mutant_df[mutant_df['Mutant_SASA_no_alanine'] >= mutant_df['SASA_no_wt_position']]
    # get the difference between the mutant sasa and the sequence sasa
    mutant_df['DimerSasaDifference'] = mutant_df['Mutant_SASA_no_alanine'] - mutant_df['SASA_no_wt_position']
    # output the mutant_df
    mutant_df.to_csv(f'{output_dir}/mutant_df_sasa_dimer_comparison.csv', index=False)
    print(len(mutant_df))

    # Step three: check if the sasa at the mutant position is exposed by comparing to polyAla
    # output the dataframe to a csv file
    mutant_df.to_csv(f'{output_dir}/{output_file}', index=False)

    # get the top 2 void mutants
    top_void_df = getTopVoidMutants(mutant_df)
    # output the dataframe to a csv file
    top_void_df.to_csv(f'{output_dir}/top_void_mutants.csv', index=False)

    # keep only mutants not found in the top_void_df
    no_void_mutant_df = start_mutant_df[~start_mutant_df['Mutant'].isin(top_void_df['Mutant'])]
    print(len(no_void_mutant_df))
    # add the df_wt_data to the mutant_df
    #mutant_df = pd.concat([mutant_df, df_wt_data], axis=0)

    # get the worst 2 void mutants
    worst_void_df = getWorstVoidMutants(no_void_mutant_df)
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

    # concat the top_void_df and worst_void_df
    void_df = pd.concat([top_void_df, worst_void_df], axis=0)
    # output the void_df
    void_df.to_csv(f'{output_dir}/all_mutants.csv', index=False)
