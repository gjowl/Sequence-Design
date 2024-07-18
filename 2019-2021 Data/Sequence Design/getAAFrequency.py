import os, sys, pandas as pd, argparse

# initialize the parser
parser = argparse.ArgumentParser(description='Gets the amino acid frequency from a sequence file')

# add the necessary arguments
parser.add_argument('-seqFile','--sequenceFile', type=str, help='the sequence file')
# add the optional arguments
parser.add_argument('-outFile','--outputFile', type=str, help='the output csv file')
parser.add_argument('-outDir','--outputDir', type=str, help='the output directory')
# extract the arguments into variables
args = parser.parse_args()
seqFile = args.sequenceFile
# default values for the optional arguments
outputFile = 'aaFrequency'
outputDir = os.getcwd()
# if the optional arguments are not specified, use the default values
if args.outputFile is not None:
    outputFile = args.outputFile
if args.outputDir is not None:
    outputDir = args.outputDir
    os.makedirs(outputDir, exist_ok=True)

if __name__ == '__main__':
    # read the sequence file
    seqDf = pd.read_csv(seqFile)

    # get the amino acid frequency
    aaFreq = seqDf['Sequence'].str.split('', expand=True).stack().value_counts()
    aaFreq = aaFreq.reset_index()
    aaFreq.columns = ['Amino Acid', 'Count']

    # remove the empty string and x from the amino acid column
    aaFreq = aaFreq[aaFreq['Amino Acid'] != '']
    aaFreq = aaFreq[aaFreq['Amino Acid'] != 'X']

    # get the sum of the counts
    total = aaFreq['Count'].sum()

    # divide the count by the total to get the frequency
    aaFreq['Frequency'] = aaFreq['Count'] / total

    # write the output dataframe to a csv file
    aaFreq.to_csv(f'{outputDir}/{outputFile}.csv', index=False)