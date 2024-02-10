import os, sys, pandas as pd, argparse, matplotlib.pyplot as plt

# initialize the parser
parser = argparse.ArgumentParser(description='Plots the data from the input datafile')

# add the necessary arguments
parser.add_argument('-inFile','--inFile', type=str, help='the raw data directory')
# add the optional arguments
parser.add_argument('-outFile','--outputFile', type=str, help='the output csv file')
parser.add_argument('-outDir','--outputDir', type=str, help='the output directory')

# extract the arguments into variables
args = parser.parse_args()
inputFile = args.inFile
# default values for the optional arguments
outputFile = 'hbondData'
outputDir = os.getcwd()
# if the optional arguments are not specified, use the default values
if args.outputDir is not None:
    outputDir = args.outputDir
    os.makedirs(outputDir, exist_ok=True)
if args.outputFile is not None:
    outputFile = args.outputFile

if __name__ == '__main__':
    # read the input file as a dataframe
    df = pd.read_csv(inputFile, sep=',', dtype={'Interface': str})
    
    yaxis = 'PercentGpA'
    #yaxis = 'toxgreen_fluor'
    cols = ['hbondDonors', 'hbondAcceptors']
    # loop through the different design regions
    for sample in df['Sample'].unique():
        df_sample = df[df['Sample'] == sample]
        # make the sample directory if it doesn't exist
        sampleDir = f'{outputDir}/{sample}'
        os.makedirs(sampleDir, exist_ok=True)
        # loop through the columns of interest
        for col in cols:
            # keep only the sequence with the highest number of potential hydrogen bonds
            df_sample = df_sample.sort_values(col, ascending=False).drop_duplicates('Sequence').sort_index()
            # plot the data
            plt.scatter(df_sample[col], df_sample[yaxis])
            plt.xlabel(col)
            plt.ylabel(yaxis)
            # set the yaxis limit to be 1/10 more than the max value
            plt.ylim(0, df[yaxis].max() + df[yaxis].max()/10)
            plt.title(f'{yaxis} vs {col}')
            plt.savefig(f'{sampleDir}/{outputFile}_{col}.png')
            plt.savefig(f'{sampleDir}/{outputFile}_{col}.svg')
            plt.close()
            # output the dataframe to a csv file without the index
            df_sample.to_csv(f'{sampleDir}/{outputFile}_{col}.csv', index=False)
