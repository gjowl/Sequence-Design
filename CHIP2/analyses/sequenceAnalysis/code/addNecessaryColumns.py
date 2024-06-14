import os, sys, pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns, argparse

# initialize the parser
parser = argparse.ArgumentParser(description='Add the necessary columns to the sequence and mutant files')

# add the necessary arguments
parser.add_argument('-seqFile','--sequenceFile', type=str, help='the input WT design csv file')
parser.add_argument('-mutFile','--mutantFile', type=str, help='the input mutant csv file')
# add the optional arguments
parser.add_argument('-outDir','--outputDir', type=str, help='the output directory')
parser.add_argument('-toxgreenFile', type=str, help='the toxgreen converted reconstruction data')

# extract the arguments into variables
args = parser.parse_args()
sequenceFile = args.sequenceFile
mutantFile = args.mutantFile
# default values for the optional arguments
outputDir = os.getcwd()
toxgreenFile = None
# if the optional arguments are not specified, use the default values
if args.outputDir is not None:
    outputDir = args.outputDir
    os.makedirs(outputDir, exist_ok=True)
if args.toxgreenFile is not None:
    toxgreenFile = args.toxgreenFile

if __name__ == '__main__':
    # read in the input files
    df_wt = pd.read_csv(sequenceFile) # wt data file
    df_mut = pd.read_csv(mutantFile) # mutant data file
    
    # check the length of sequence
    sequenceLength = len(df_wt['Sequence'].values[0])
    if sequenceLength < 21:
        # add LLL and ILI to the sequence
        df_wt['Sequence'] = df_wt.apply(lambda row: 'LLL' + row['Sequence'] + 'ILI', axis=1)
        df_mut['Sequence'] = df_mut.apply(lambda row: 'LLL' + row['Sequence'] + 'ILI', axis=1)
    
    # add the toxgreen/reconstructed data if not present
    if toxgreenFile is not None:
        # read in the reconstructed data
        df_toxgreen = pd.read_csv(toxgreenFile)
        # merge the reconstructed data with the wt data
        df_wt = df_wt.merge(df_toxgreen[['Sequence', 'Sample', 'PercentGpA_transformed', 'std_adjusted', 'toxgreen_fluor', 'toxgreen_std']], on='Sequence', how='left')
        # merge the reconstructed data with the mutant data
        df_mut = df_mut.merge(df_toxgreen[['Sequence', 'Sample', 'PercentGpA_transformed', 'std_adjusted', 'toxgreen_fluor', 'toxgreen_std']], on='Sequence', how='left')

    # rename the Sequence column to Mutant for the mutant dataframe
    df_mut.rename(columns={'Sequence': 'Mutant'}, inplace=True)
    df_mut.rename(columns={'WT Sequence': 'Sequence'}, inplace=True)
    
    # remove redundant sequences from the wt dataframe
    df_wt = df_wt.drop_duplicates(subset='Sequence')
    # remove redundant sequence, mutant pairs from the mutant dataframe
    df_mut = df_mut.drop_duplicates(subset=['Sequence', 'Mutant'])
    
    # get the position of the mutation between the sequence column and disruptive mutant column
    df_wt['Position'] = df_wt.apply(lambda row: [i for i in range(1, len(row['Sequence'])+1) if row['Sequence'][i-1] != row['Clash Mutant'][i-1]][0], axis=1)
    df_wt['Position'] = df_wt['Position'].astype(int)-1 # subtract 1 to the position to account for starting at 0
    
    # added in for GASrights (some mutants don't have the position, so just regetting it here)
    df_mut['Position'] = df_mut.apply(lambda row: [i for i in range(1, len(row['Sequence'])+1) if row['Sequence'][i-1] != row['Mutant'][i-1]][0], axis=1)
    df_mut['Position'] = df_mut['Position'].astype(int)-1 # subtract 1 to the position to account for starting at 0
    
    # Add the WT_AA column to the mutant dataframe
    df_wt['WT_AA'] = df_wt.apply(lambda row: row['Sequence'][row['Position']], axis=1)
    df_mut['WT_AA'] = df_mut.apply(lambda row: row['Sequence'][row['Position']], axis=1)
    
    # add the mutAA column to the mutant dataframe
    df_mut['mut_AA'] = df_mut.apply(lambda row: row['Mutant'][row['Position']], axis=1)
    df_wt['mut_AA'] = df_wt.apply(lambda row: row['Clash Mutant'][row['Position']], axis=1)
    
    df_wt.rename(columns={'Clash Mutant': 'Mutant'}, inplace=True)
    
    # keep only the sequences that are present in the wt dataframe
    df_mut = df_mut[df_mut['Sequence'].isin(df_wt['Sequence'].unique())]
    
    df_wt.to_csv(f'{outputDir}/wt.csv', index=False)
    df_mut.to_csv(f'{outputDir}/mutant.csv', index=False)
    
    # check if PercentGpA is a column, else names need to be converted
    if 'PercentGpA' not in df_wt.columns:
        df_wt['PercentGpA'] = df_wt['PercentGpA_transformed']
        df_mut['PercentGpA'] = df_mut['PercentGpA_transformed']
        df_wt['PercentStd'] = df_wt['std_adjusted']
        df_mut['PercentStd'] = df_mut['std_adjusted']
    
    # combine the files with the given columns
    cols = ['Sample', 'Sequence', 'Mutant', 'Position', 'Type', 'Mutant Type', 'WT_AA', 'mut_AA', 'PercentGpA', 'PercentStd', 'toxgreen_fluor', 'toxgreen_std']
    
    # add in wt data for each mutant, since the wt data only includes the best clash mutant for each sequence
    # change the mutant type to wt
    df_copy_wt = df_mut.copy()
    df_copy_wt['Type'] = 'WT'
    copyCols = ['PercentGpA', 'PercentStd', 'toxgreen_fluor', 'toxgreen_std']
    # get the values from the wt dataframe for each sequence
    df_copy_wt['PercentGpA'] = df_copy_wt.apply(lambda row: df_wt[df_wt['Sequence'] == row['Sequence']]['PercentGpA'].values[0], axis=1)
    df_copy_wt['PercentStd'] = df_copy_wt.apply(lambda row: df_wt[df_wt['Sequence'] == row['Sequence']]['PercentStd'].values[0], axis=1)
    df_copy_wt['toxgreen_fluor'] = df_copy_wt.apply(lambda row: df_wt[df_wt['Sequence'] == row['Sequence']]['toxgreen_fluor'].values[0], axis=1)
    df_copy_wt['toxgreen_std'] = df_copy_wt.apply(lambda row: df_wt[df_wt['Sequence'] == row['Sequence']]['toxgreen_std'].values[0], axis=1)
    
    # output the wt and mutant dataframes
    df_copy_wt = df_copy_wt[cols].copy()
    df_all = pd.concat([df_wt[cols], df_mut[cols], df_copy_wt[cols]])
    df_all.to_csv(f'{outputDir}/all.csv', index=False)
    
    # check if each sequence has at least 1 void and 1 clash in the Mutant Type column
    df_mut['Void'] = df_mut['Mutant Type'].apply(lambda x: 'void' in x)
    df_mut['Clash'] = df_mut['Mutant Type'].apply(lambda x: 'clash' in x)
    df_void = df_mut[df_mut['Void'] == True]
    df_clash = df_mut[df_mut['Clash'] == True]
    
    # keep only sequences that are present in both the void and clash dataframes (at least 1 void and 1 clash mutant per sequence)
    df_c_v = df_void[df_void['Sequence'].isin(df_clash['Sequence'].unique())]
    df_wt_cv = df_wt[df_wt['Sequence'].isin(df_c_v['Sequence'].unique())]
    df_mut_cv = df_mut[df_mut['Sequence'].isin(df_c_v['Sequence'].unique())]
    df_copy_wt_cv = df_copy_wt[df_copy_wt['Sequence'].isin(df_c_v['Sequence'].unique())]
    
    # add the pos_wtAA and pos_mutAA columns
    output_df = pd.concat([df_wt_cv[cols], df_mut_cv[cols], df_copy_wt_cv[cols]])
    output_df['pos_wtAA'] = output_df['Position'].astype(str) + output_df['WT_AA']
    output_df['pos_mutAA'] = output_df['Position'].astype(str) + output_df['mut_AA']
    output_df['WT_MUT'] = output_df['WT_AA'] + output_df['mut_AA']
    output_df.to_csv(f'{outputDir}/all.csv', index=False)
    
    # add the mutant percent gpA column by searching for the mutant sequence in the output dataframe
    df_deltaPercentGpA = df_mut_cv.copy()
    df_deltaPercentGpA['WT Fluor'] = df_mut_cv.apply(lambda row: df_wt_cv[df_wt_cv['Sequence'] == row['Sequence']]['toxgreen_fluor'].values[0], axis=1)
    df_deltaPercentGpA['Delta Fluorescence'] = df_deltaPercentGpA['WT Fluor'] - df_deltaPercentGpA['toxgreen_fluor']
    df_deltaPercentGpA['WT PercentGpA'] = df_mut_cv.apply(lambda row: df_wt_cv[df_wt_cv['Sequence'] == row['Sequence']]['PercentGpA'].values[0], axis=1)
    df_deltaPercentGpA['Delta PercentGpA'] = df_deltaPercentGpA['WT PercentGpA'] - df_deltaPercentGpA['PercentGpA']
    cols.append('WT Fluor')
    cols.append('Delta Fluorescence')
    cols.append('WT PercentGpA')
    cols.append('Delta PercentGpA')
    df_deltaPercentGpA = df_deltaPercentGpA[cols].copy()
    # for the rows that delta fluorescence is 0, get the mutant 
    df_deltaPercentGpA.to_csv(f'{outputDir}/deltaFluorescence.csv', index=False)