import os, sys, pandas as pd, numpy as np, argparse
import matplotlib.pyplot as plt

# initialize the parser
parser = argparse.ArgumentParser(description='Compare the vdw and sasa of mutants to the WT sequence')
parser.add_argument('-wt','--wtFile', type=str, help='the input reconstructed fluorescence csv file')
parser.add_argument('-mut','--mutFile', type=str, help='the input mutant csv file')
parser.add_argument('-outDir','--outputDir', type=str, help='the output directory')

# extract the arguments into variables
args = parser.parse_args()
# necessary arguments
wtFile = args.wtFile
mutFile = args.mutFile
# optional arguments
outputDir = os.getcwd()
if args.outputDir is not None:
    outputDir = args.outputDir
    os.makedirs(outputDir, exist_ok=True)

if __name__ == '__main__':
    # read in the data
    wt = pd.read_csv(wtFile)
    mut = pd.read_csv(mutFile)

    # rid of proteins that have a positive energy
    wt = wt[wt['VDWDiff'] < 0]

    # add LLL and ILI to the end of the sequences
    wt['Sequence'] = wt['Sequence'].apply(lambda x: 'LLL' + x + 'ILI')
    # replace the first 3 characters of the sequence with LLL for the mutant data
    mut['Sequence'] = mut['Sequence'].str[3:-3]
    mut['Sequence'] = mut['Sequence'].apply(lambda x: 'LLL' + x + 'ILI')
    mut['Mutant'] = mut['Mutant'].str[3:-3]
    mut['Mutant'] = mut['Mutant'].apply(lambda x: 'LLL' + x + 'ILI')

    # calculate the SASA
    sasaCol = 'interfaceSasa'
    output_df = pd.DataFrame()
    # loop through the wt data and compare to the mutant data
    for seq in wt['Sequence'].unique():
        # get the wt data
        wt_seq = wt[wt['Sequence'] == seq]
        # get the mutant data
        tmp_mut = mut[mut['Sequence'] == seq]
        #wt_sasa_1 = wt_seq[sasaCol].values[0]
        sample = wt_seq['Sample'].values[0]
        for m in tmp_mut['Mutant']:
            # find the position different between the wt and mutant sequences
            pos = [i for i in range(len(seq)) if seq[i] != m[i]]
            # get that character from the wt sequence and mutant sequence
            wt_char = seq[pos[0]]
            mut_char = m[pos[0]]
            wt_mut = f'{wt_char}{mut_char}'
            # get the wt sasa
            wt_monomer = tmp_mut[tmp_mut['Mutant'] == m]['WT_MonomerSasa'].values[0]
            wt_dimer = tmp_mut[tmp_mut['Mutant'] == m]['WT_DimerSasa'].values[0]
            wt_sasa = wt_monomer - wt_dimer
            # get the mutant sasa
            mut_monomer = tmp_mut[tmp_mut['Mutant'] == m]['Mutant_MonomerSasa'].values[0]
            mut_dimer = tmp_mut[tmp_mut['Mutant'] == m]['Mutant_DimerSasa'].values[0]
            mut_sasa = mut_monomer - mut_dimer
            # subtract the wt_sasa from the mutant sasa for the current m
            sasa_perc = mut_sasa / wt_sasa
            output_df = pd.concat([output_df, pd.DataFrame({'WT Sequence': seq, 'Mutant Sequence': m, 'Region': sample, 'WTAA': wt_char, 'MutAA': mut_char, 'WT_MUT': wt_mut, 'Position': pos, 'SASA Percent': sasa_perc})])
    # save the dataframes
    output_df.to_csv(f'{outputDir}/allDifferences.csv', index=False)

    # get counts for each unique value in the wt_mut column of the clash dataframe
    void_df = output_df[output_df['MutAA'] == 'A']
    void_df.to_csv(f'{outputDir}/voidDifferences.csv', index=False)
    #clash_counts = clash_df['WT_MUT'].value_counts()
    #clash_counts.to_csv(f'{outputDir}/clashCounts.csv')
    # get the average SASA difference for each unique value in the wt_mut column of the clash dataframe
    void_avg = void_df.groupby('WT_MUT')['SASA Percent'].mean()
    void_avg.to_csv(f'{outputDir}/voidAvg.csv')

    # sort the dataframe by the wt_mut column
    void_df = void_df.sort_values('WT_MUT')
    # plot the individual SASA differences for each unique value in the wt_mut column of the clash dataframe
    void_df.boxplot(column='SASA Percent', by='WT_MUT', rot=90)
    # plot the points on top of the boxplot in the same order as the boxplot
    for i in range(len(void_df['WT_MUT'].unique())):
        y = void_df[void_df['WT_MUT'] == void_df['WT_MUT'].unique()[i]]['SASA Percent']
        x = np.random.normal(i+1, 0.04, size=len(y))
        plt.plot(x, y, '.', color='black', markersize=2)
    plt.title('SASA Difference for Void Mutants')
    plt.xlabel('WT_MUT')
    plt.ylabel('Percent SASA of WT')
    plt.savefig(f'{outputDir}/voidAvgPlot.png')
    plt.savefig(f'{outputDir}/voidAvgPlot.svg')

    # get counts for each unique value in the wt_mut column of the void dataframe
    void_counts = void_df['WT_MUT'].value_counts()
    void_counts.to_csv(f'{outputDir}/voidCounts.csv')