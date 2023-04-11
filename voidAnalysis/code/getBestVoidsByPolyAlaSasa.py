import os, sys, pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def getTopVoidMutants(df, numMutants=2):
    output_df = pd.DataFrame()
    for seq in df['Sequence'].unique():
        # loop through the sequences
        seq_df = df[df['Sequence'] == seq]
        # keep the sequences with the top 2 SasaDiff values
        seq_df = seq_df.nlargest(numMutants, 'SasaDifference')
        # concat the directory_df to the top_void_df
        output_df = pd.concat([output_df, seq_df], axis=0)
    return output_df

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
    # read in the command line arguments
    mutant_file = sys.argv[1]
    polyAla_file = sys.argv[2]
    output_file = sys.argv[3]

    # read in the csv file as a dataframe
    mutant_df = pd.read_csv(mutant_file, sep=',', header=0, dtype={'Interface': 'str'})
    polyAla_df = pd.read_csv(polyAla_file, sep=',', header=None)
    # multiply the polyAla values by 2 to get the total sasa (currently loads up monomer sasa file)
    polyAla_df = polyAla_df * 2

    # find positions in sequence that are not the same in the mutant
    mutant_df['Position'] = mutant_df.apply(lambda row: [i for i in range(len(row['Sequence'])) if row['Sequence'][i] != row['Mutant'][i]], axis=1)
    # convert the position column to an integer
    mutant_df['Position'] = mutant_df['Position'].apply(lambda x: int(x[0]))

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
        mutant_sasa = mutant_df[mutant_df['Mutant'] == mutant]['Mutant_AA'].values[0]
        # get the difference between the polyAla and the mutant sasa
        sasaDiff = polyAla - mutant_sasa
        # append the difference to the sasaDiff list
        sasaDiff_list.append(sasaDiff)
        # get the sasa percentage difference
        sasaPercDiff = (mutant_sasa / polyAla) * 100
        # append the sasa percentage difference to the sasaPercDiff list
        sasaPercDiff_list.append(sasaPercDiff)

    # add the SasaPercDifference to the mutant_df dataframe
    mutant_df['SasaPercDifference'] = sasaPercDiff_list
    # add the SasaDifference to the mutant_df dataframe
    mutant_df['SasaDifference'] = sasaDiff_list

    # output the dataframe to a csv file
    mutant_df.to_csv(output_file, index=False) 

    # get the top 2 void mutants
    top_void_df = getTopVoidMutants(mutant_df)
    # output the dataframe to a csv file
    top_void_df.to_csv('top_void_mutants.csv', index=False)

    # get the worst 2 void mutants
    worst_void_df = getWorstVoidMutants(mutant_df)
    # output the dataframe to a csv file
    worst_void_df.to_csv('worst_void_mutants.csv', index=False)

    # get the count of void mutants for each interface
    count_df = top_void_df.groupby(['Interface', 'Position'])['Mutant'].count().reset_index()
    # plot the position of the void mutants on the y axis with the interface on the x axis
    plt.scatter(count_df['Interface'], count_df['Position'], c=count_df['Mutant'], cmap='RdYlGn')
    plt.xlabel('Interface')
    plt.ylabel('Position')
    plt.title('Position of Void Mutants on Interface against count')
    plt.colorbar()
    # fit the interface names to the plot
    # set y axis to be integers
    plt.gca().set_yticks(range(0, 20))
    # decrease the size of the x axis labels
    plt.gca().tick_params(axis='x', labelsize=6, labelrotation=45)
    plt.tight_layout()
    plt.savefig('void_mutants_position_count.png', dpi=500)

    plt.clf()
    # get the average SasaDifference for each position for each interface
    avg_df = mutant_df.groupby(['Interface', 'Position'])['SasaDifference'].mean().reset_index()
    # plot the position of the void mutants on the y axis with the interface on the x axis
    plt.scatter(avg_df['Interface'], avg_df['Position'], c=avg_df['SasaDifference'], cmap='RdYlGn')
    plt.xlabel('Interface')
    plt.ylabel('Position')
    plt.title('Position of Void Mutants on Interface')
    plt.colorbar()
    # fit the interface names to the plot
    plt.tight_layout()
    plt.savefig('void_mutants_position.png', dpi=500)
    plt.clf()

    # make a boxplot of the SasaDifference for each position for each interface
    for interface in mutant_df['Interface'].unique():
        interface_df = mutant_df[mutant_df['Interface'] == interface]
        # plot the boxplot for each position
        sns.boxplot(x='Position', y='SasaPercDifference', data=interface_df)
        plt.xlabel('Position')
        plt.ylabel('SasaDifference')
        plt.title(f'SasaDifference for each position on interface {interface}')
        # set the y axis to be from 0-100
        plt.ylim(0, 100)
        plt.savefig(f'void_mutants_sasadiff_{interface}.png', dpi=500)
        plt.clf()

    # keep the void mutants with a SasaDifference == 0
    void_df = mutant_df[mutant_df['Mutant_AA'] == 0]
    # output the dataframe to a csv file
    void_df.to_csv('void_mutants_0.csv', index=False)


