import os, sys, pandas as pd, numpy as np, argparse

# initialize the parser
parser = argparse.ArgumentParser(description='Appends the input datafile with the toxgreen data from another input datafile')

# add the necessary arguments
parser.add_argument('-inFile','--inputFile', type=str, help='the input csv file')
parser.add_argument('-maltoseFile','--maltoseFile', type=str, help='the maltose csv file')
parser.add_argument('-outFile','--outputFile', type=str, help='the output csv file')
parser.add_argument('-maltoseCol','--maltoseCol', type=str, help='the column to use for maltose trimming')
# add the optional arguments
parser.add_argument('-outDir','--outputDir', type=str, help='the output directory')

# extract the arguments into variables
args = parser.parse_args()
dataFile = args.inputFile
maltoseFile = args.maltoseFile
maltoseCol = args.maltoseCol
outputFile = args.outputFile
# default values for the optional arguments
outputDir = os.getcwd()
# if the optional arguments are not specified, use the default values
if args.outputDir is not None:
    outputDir = args.outputDir
    os.makedirs(outputDir, exist_ok=True)

if __name__ == '__main__':
    # read in the data
    data = pd.read_csv(dataFile)
    maltose = pd.read_csv(maltoseFile)

    # keep the maltose data for Segments N
    neg_maltose = maltose[maltose['Segments'] == 'N']
    highest_maltose = neg_maltose[maltoseCol].max()

    # only keep sequences that pass the maltose test
    maltose_passing_data = maltose[maltose[maltoseCol] >= highest_maltose]
    maltose_passing_sequences = maltose_passing_data['Sequence']

    # remove the first 3 amino acids from the sequence (since the data file has the first 3 amino acids removed)
    maltose_passing_sequences = [x[3:] for x in maltose_passing_sequences]

    # keep only the data passing the maltose test
    data = data[data['Sequence'].isin(maltose_passing_sequences)]

    # output the dataframe to a csv file
    data.to_csv(f'{outputDir}/{outputFile}.csv', sep=',', index=False)

