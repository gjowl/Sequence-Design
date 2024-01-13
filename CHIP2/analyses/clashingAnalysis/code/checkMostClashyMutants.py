import os, sys, pandas as pd, numpy as np, matplotlib.pyplot as plt, argparse

# initialize the parser
parser = argparse.ArgumentParser(description='Keeps the data for WT sequences that have mutants with a lower fluorescence')

# add the necessary arguments
parser.add_argument('-seqFile','--sequenceFile', type=str, help='the input WT design csv file')
parser.add_argument('-mutFile','--mutantFile', type=str, help='the input mutant csv file')
parser.add_argument('-outDir','--outputDir', type=str, help='the output directory')
# add the optional arguments
parser.add_argument('-wtCutoff','--wtFluorCutoff', type=float, help='the cutoff for the WT fluorescence')
parser.add_argument('-mutantCutoff','--mutantFluorCutoff', type=float, help='the cutoff for the mutant fluorescence')
#parser.add_argument('-numMutants','--numberMutants', type=int, help='the number of mutants necessary to be accepted for the WT design to be accepted')

# extract the arguments into variables
args = parser.parse_args()
sequenceFile = args.sequenceFile
mutantFile = args.mutantFile
# default values for the optional arguments
outputDir = os.getcwd()
wtFluorCutoff = 0.35
mutantFluorCutoff = 0.35
#numberMutants = 0

# if the optional arguments are not specified, use the default values
if args.outputDir is not None:
    outputDir = args.outputDir
    os.makedirs(outputDir, exist_ok=True)
if args.wtFluorCutoff is not None:
    wtFluorCutoff = args.wtFluorCutoff
if args.mutantFluorCutoff is not None:
    mutantFluorCutoff = args.mutantFluorCutoff
#if args.numberMutants is not None:
#    numberMutants = args.numberMutants

if __name__ == '__main__': 
    # read in the input files 
    df_wt = pd.read_csv(sequenceFile) # wt data file
    df_mut = pd.read_csv(mutantFile) # mutant data file
    yAxis = [col for col in df_wt.columns if 'transformed' in col][0] # get the PercentGpA column
    sort_col = yAxis
    sortAscending = True 

    # setup the output dataframes
    output_df = pd.DataFrame()
    output_mutant_df = pd.DataFrame()

    # loop through the wt sequences 
    for sequence in df_wt['Sequence'].unique():
        tmp_wt = df_wt[df_wt['Sequence'] == sequence]
        # get only the best sequence
        if len(tmp_wt) > 1:
            tmp_wt = tmp_wt.sort_values(by=[sort_col], ascending=False)
            tmp_wt = tmp_wt.drop_duplicates(subset='Sequence', keep='first')
        # get the mutants for this sequence and get the lowest energy mutant
        tmp_mut = df_mut[df_mut['Sequence'] == sequence]
        if len(tmp_mut) < 1:
            continue # skip if there are no mutants
        tmp_mut = tmp_mut.sort_values(by=[sort_col], ascending=sortAscending)
        # check if the fluorescence of the WT is greater than the mutant
        wt_fluor = tmp_wt[yAxis].values[0]
        if wt_fluor < wtFluorCutoff:
            continue # skip if the WT fluorescence is too low
        mutant_fluor = tmp_mut[yAxis].values[0]
        percentWT = mutant_fluor / wt_fluor * 100
        if mutant_fluor > mutantFluorCutoff:
            continue # skip if the mutant fluorescence is too high
        # get the mutant sequence
        mutant_seq = tmp_mut['Mutant'].values[0]
        # add it to the tmp_wt dataframe
        tmp_wt['Disruptive Mutant'] = mutant_seq
        wt_seq = tmp_wt['Sequence'].values[0]
        tmp_mut['WT Sequence'] =  wt_seq
        tmp_wt['Mutant Type'] = tmp_mut['Mutant Type'].values[0]
        # add the sequence to the output dataframe
        output_df = pd.concat([output_df, tmp_wt], axis=0)
        output_mutant_df = pd.concat([output_mutant_df, tmp_mut], axis=0)

    # add the type column to the output dataframes to distinguish between WT and mutant
    output_df['Type'] = 'WT'
    output_mutant_df['Type'] = 'Mutant'

    # rename the mutant and sequence columns for the output_mutant_df
    output_mutant_df = output_mutant_df.rename(columns={'Sequence': 'WTSequence'})
    output_mutant_df = output_mutant_df.rename(columns={'Mutant': 'Sequence'})
    output_df_all = pd.concat([output_df, output_mutant_df], axis=0)
    output_df.to_csv(f'{outputDir}/wt.csv', index=False)
    output_mutant_df.to_csv(f'{outputDir}/mutant.csv', index=False)
    output_df_all.to_csv(f'{outputDir}/all.csv', index=False)
    print(f'Number of WT sequences with mutants less than {mutantFluorCutoff}: {len(output_df)}')