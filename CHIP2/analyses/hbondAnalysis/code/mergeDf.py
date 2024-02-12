import os, sys, pandas as pd, argparse

# initialize the parser
parser = argparse.ArgumentParser(description='Appends the input datafile with the toxgreen data from another input datafile')

# add the necessary arguments
parser.add_argument('-inFile','--inFile', type=str, help='the raw data directory')
parser.add_argument('-fileToMerge','--fileToMerge', type=str, help='the file with the data to merge')
parser.add_argument('-outFile','--outputFile', type=str, help='the output csv file')
# add the optional arguments
parser.add_argument('-outDir','--outputDir', type=str, help='the output directory')

# extract the arguments into variables
args = parser.parse_args()
inputFile = args.inFile
mergeFile = args.fileToMerge
outputFile = args.outputFile
# default values for the optional arguments
outputDir = os.getcwd()
# if the optional arguments are not specified, use the default values
if args.outputDir is not None:
    outputDir = args.outputDir
    os.makedirs(outputDir, exist_ok=True)

if __name__ == '__main__':
    # read the input file and the file to merge as dataframes
    df = pd.read_csv(inputFile, sep=',', dtype={'Interface': str})
    mergeDf = pd.read_csv(mergeFile)

    # merge df with mergeDf by the 'Sequence' column
    df = pd.merge(df, mergeDf, on='Sequence', how='left')

    # output the dataframe to a csv file without the index
    df.to_csv(f'{outputDir}/{outputFile}.csv', index=False)