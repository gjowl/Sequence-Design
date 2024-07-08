import os, sys, pandas as pd, numpy as np, argparse

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
    mut['Sequence'] = mut['Sequence'].apply(lambda x: 'LLL' + x + 'ILI')

    # calculate the SASA
    sasaCol = 'SASA'
    wt[sasaCol] = wt['MonomerSasa'] - wt['OptimizeSasa']
    mut[sasaCol] = mut['MonomerSasa'] - mut['OptimizeSasa']
    # initialize the dataframes
    clash_df = pd.DataFrame()
    void_df = pd.DataFrame()

    # create a list of mutant types
    mut_types = ['clash', 'void']
    # loop through the wt data and compare to the mutant data
    for seq in wt['Sequence'].unique():
        # get the wt data
        wt_seq = wt[wt['Sequence'] == seq]
        # get the mutant data
        mut_seq = mut[mut['WT Sequence'] == seq]
        # get the wt VDW and SASA
        wt_vdw = wt_seq['VDWDiff'].values[0]
        wt_sasa = wt_seq[sasaCol].values[0]
        sample = wt_seq['Sample'].values[0]
        for mut_type in mut_types:
            # get the type of mutant
            tmp_mut = mut_seq[mut_seq['Mutant Type'] == mut_type]
            for m in tmp_mut['Sequence']:
                # find the position different between the wt and mutant sequences
                pos = [i for i in range(len(seq)) if seq[i] != m[i]]
                # get that character from the wt sequence and mutant sequence
                wt_char = seq[pos[0]]
                mut_char = m[pos[0]]
                wt_mut = f'{wt_char}{mut_char}'
                mut_vdw = tmp_mut[tmp_mut['Sequence'] == m]['VDWDiff'].values[0]
                # subtract the wt_vdw from the mutant vdw
                vdw_diff = tmp_mut[tmp_mut['Sequence'] == m]['VDWDiff'].values[0] - wt_vdw
                # subtract the wt_sasa from the mutant sasa
                sasa_diff = tmp_mut[tmp_mut['Sequence'] == m][sasaCol].values[0] - wt_sasa
                if mut_type == 'clash':
                    # add the data to the clash dataframe using the pd.concat function
                    clash_df = pd.concat([clash_df, pd.DataFrame({'WT Sequence': seq, 'Mutant Sequence': m, 'Region': sample, 'WTAA': wt_char, 'MutAA': mut_char, 'WT_MUT': wt_mut, 'Position': pos, 'VDW Difference': vdw_diff, 'SASA Difference': sasa_diff})])
                elif mut_type == 'void':
                    if mut_vdw > 0:
                        # for some reason some of my sequences have a positive vdw difference, so I'm going to skip those (I think I must have ran a set on a day where the outputs were fucked, so maybe will rerun those)
                        continue
                    void_df = pd.concat([void_df, pd.DataFrame({'WT Sequence': seq, 'Mutant Sequence': m, 'Region': sample, 'WTAA': wt_char, 'MutAA': mut_char, 'WT_MUT': wt_mut, 'Position': pos, 'VDW Difference': vdw_diff, 'SASA Difference': sasa_diff})])
    # save the dataframes
    clash_df.to_csv(f'{outputDir}/clashDifferences.csv', index=False)
    void_df.to_csv(f'{outputDir}/voidDifferences.csv', index=False)

    # get counts for each unique value in the wt_mut column of the clash dataframe
    clash_counts = clash_df['WT_MUT'].value_counts()
    clash_counts.to_csv(f'{outputDir}/clashCounts.csv')

    # get counts for each unique value in the wt_mut column of the void dataframe
    void_counts = void_df['WT_MUT'].value_counts()
    void_counts.to_csv(f'{outputDir}/voidCounts.csv')