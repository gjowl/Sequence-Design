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
parser.add_argument('-sequenceColumn','--sequenceColumn', type=str, help='the column name for the sequence') # added because the mutant file has a different column name for the sequence of interest
parser.add_argument('-maltoseSeq','--maltoseSeq', type=str, help='the sequence to use for maltose trimming')

# extract the arguments into variables
args = parser.parse_args()
dataFile = args.inputFile
maltoseFile = args.maltoseFile
maltoseCol = args.maltoseCol
outputFile = args.outputFile
# default values for the optional arguments
outputDir = os.getcwd()
sequenceColumn = 'Sequence'
maltoseSeq = None
# if the optional arguments are not specified, use the default values
if args.outputDir is not None:
    outputDir = args.outputDir
    os.makedirs(outputDir, exist_ok=True)
if args.sequenceColumn is not None:
    sequenceColumn = args.sequenceColumn
# check if maltoseSeq is longer than 4 characters
if len(args.maltoseSeq) > 4: # I think even when None gets passed as an option, it's a string. Sequences are longer than 4 characters, so this should work
    maltoseSeq = args.maltoseSeq

if __name__ == '__main__':
    # read in the data
    data = pd.read_csv(dataFile, dtype={'Interface': str})
    maltose = pd.read_csv(maltoseFile)

    # keep the maltose data for Segments N
    # if the maltose sequence is specified, use that sequence to filter the data
    if maltoseSeq is None:
        print('No maltose sequence specified, using the highest known maltose value (N in Segments) to filter the data')
        neg_maltose = maltose[maltose['Segments'] == 'N']
        highest_maltose = neg_maltose[maltoseCol].max()
    else:
        neg_maltose = maltose[maltose['Sequence'] == maltoseSeq]
        highest_maltose = neg_maltose[maltoseCol].max()

    # only keep sequences that pass the maltose test
    maltose_passing_data = maltose[maltose[maltoseCol] >= highest_maltose]

    # if the sequence column is not the default, change the column name
    if sequenceColumn != 'Sequence':
        maltose_passing_data = maltose_passing_data.rename(columns={'Sequence': sequenceColumn})
    # remove the first 3 amino acids from the sequence (since the data file has the first 3 amino acids removed)
    maltose_passing_data[sequenceColumn] = [x[3:] for x in maltose_passing_data[sequenceColumn]]
    maltose_passing_sequences = maltose_passing_data[sequenceColumn]

    # check if columns from the maltose file are in the data file outside of the Sequence column
    cols = [col for col in maltose_passing_data.columns if col != sequenceColumn]
    # remove any columns that from the data file that are in the maltose file
    data = data.drop(columns=cols, errors='ignore')

    # check the length of the longest sequence in the data file vs the maltose file
    max_sequence_length = data[sequenceColumn].str.len().max()
    max_maltose_sequence_length = maltose_passing_data[sequenceColumn].str.len().max()
    # if the longest sequence in the maltose file is longer than the longest sequence in the data file, print a warning
    if max_sequence_length > max_maltose_sequence_length:
        print('Warning: The longest sequence in the maltose file is longer than the longest sequence in the data file. The sequences in the data file will be truncated to the length of the longest sequence in the maltose file.')
        # trim the sequences in the data file to the length of the longest sequence in the data file
        data[sequenceColumn] = [x[3:18] for x in data[sequenceColumn]] # I designed with different ends, so I need to trim the sequence ends off

    # keep only the data passing the maltose test and merge the data
    data = data[data[sequenceColumn].isin(maltose_passing_sequences)]
    data = data.merge(maltose_passing_data, on=sequenceColumn, how='left')

    # check if the original sequence column was changed
    if max_sequence_length > max_maltose_sequence_length:
        # add LLL to the sequence at the front and ILI to the sequence column name at the end
        data[sequenceColumn] = ['LLL' + x + 'ILI' for x in data[sequenceColumn]]

    # output the dataframe to a csv file
    data.to_csv(f'{outputDir}/{outputFile}.csv', sep=',', index=False)

