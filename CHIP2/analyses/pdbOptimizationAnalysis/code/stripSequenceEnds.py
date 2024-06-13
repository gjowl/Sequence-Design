import os, sys, pandas as pd, argparse

# initialize the parser
parser = argparse.ArgumentParser(description='Strips the first and last 3 residues from the sequence column of a csv file; used for comparing sequences that were designed with different ends (alanine vs leucine)')

# add the necessary arguments
parser.add_argument('-inFile','--inputFile', type=str, help='the input csv file')
parser.add_argument('-outFile','--outputFile', type=str, help='the output csv file')
# add the optional arguments
parser.add_argument('-outDir','--outputDir', type=str, help='the output directory')

# extract the arguments into variables
args = parser.parse_args()
inputFile = args.inputFile
outputFile = args.outputFile
# default values for the optional arguments
outputDir = os.getcwd()
# if the optional arguments are not specified, use the default values
if args.outputDir is not None:
    outputDir = args.outputDir
    os.makedirs(outputDir, exist_ok=True)

if __name__ == '__main__':
    # read in the input file as a dataframe
    df = pd.read_csv(inputFile)

    # remove the first and last 6 residues
    df['Sequence'] = df['Sequence'].apply(lambda x: x[3:-3])
    #cols = ['Sequence', 'PercentGpA_transformed', 'std_adjusted','Total','VDWDiff','HBONDDiff','IMM1Diff','Sample','LB-12H_M9-36H']
    cols = ['Sequence', 'PercentGpA_transformed', 'std_adjusted','Sample','toxgreen_fluor','toxgreen_std']
    # check if all of the columns are in the dataframe
    if not all([col in df.columns for col in cols]):
        print(f'Not all of the columns {cols} are in the dataframe, only using the ones that are present.')
        cols = [col for col in cols if col in df.columns]
    df = df[cols]
    # rename the columns
    df = df.rename(columns={'PercentGpA_transformed': 'PercentGpA', 'std_adjusted': 'PercentStd'})
    # write the output file
    df.to_csv(f'{outputDir}/{outputFile}.csv', index=False)