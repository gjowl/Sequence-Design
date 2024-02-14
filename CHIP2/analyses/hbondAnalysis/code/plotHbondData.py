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

    yaxes = []
    if 'toxgreen_fluor' in df.columns:
        yaxes.append('toxgreen_fluor')
    if 'PercentGpA' in df.columns:
        yaxes.append('PercentGpA')
    else:
        print('No columns for the yaxis found: toxgreen_fluor or PercentGpA. Exiting.')
        sys.exit(1)

    cols = ['hbonds', 'hbondDonors', 'hbondAcceptors', 'c-alphaDonors', 'c-alphaAcceptors']

    # loop through the different design regions
    for sample in df['Sample'].unique():
        df_sample = df[df['Sample'] == sample]
        # make the sample directory if it doesn't exist
        sampleDir = f'{outputDir}/{sample}'
        os.makedirs(sampleDir, exist_ok=True)
        # loop through the columns of interest
        for col in cols:
            xhigh = df_sample[col].max() 
            # keep only the sequence with the highest number of potential hydrogen bonds
            df_sample = df_sample.sort_values(col, ascending=False).drop_duplicates('Sequence').sort_index()
            # count the number of points by the column value
            count = df_sample[col].value_counts()
            # count the number of points by the column value above 40 PercentGpA
            count_cutoff = df_sample[df_sample['PercentGpA'] > 0.4][col].value_counts()
            for yaxis in yaxes:
                # plot the data
                plt.scatter(df_sample[col], df_sample[yaxis])
                plt.xlabel(col)
                plt.ylabel(yaxis)
                # set the xaxis limits
                plt.xlim(-0.5, xhigh+1)
                # set the xaxis display to be integers separated by 1
                plt.xticks(range(0, int(xhigh)+1, 1))
                # set the yaxis limit to be 1/10 more than the max value
                plt.ylim(0, df[yaxis].max() + df[yaxis].max()/10)
                # write the number of points for each value of the column
                for i in range(len(count)):
                    try:
                        plt.text(count.index[i], df_sample[yaxis].max()+df_sample[yaxis].max()/100, f'{count[i]}')
                        plt.text(count.index[i], df_sample[yaxis].max()+df_sample[yaxis].max()/10, f'{count_cutoff[i]}', color='red')
                    except KeyError:
                        pass
                plt.title(f'{yaxis} vs {col}')
                plt.savefig(f'{sampleDir}/{outputFile}_{yaxis}_{col}.png')
                plt.savefig(f'{sampleDir}/{outputFile}_{yaxis}_{col}.svg')
                plt.close()
                # output the dataframe to a csv file without the index
                df_sample.to_csv(f'{sampleDir}/{outputFile}_{yaxis}_{col}.csv', index=False)
            
