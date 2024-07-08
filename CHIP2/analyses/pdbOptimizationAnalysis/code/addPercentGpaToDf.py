import os, sys, pandas as pd, argparse

"""
 This script will append the input datafile with the toxgreen data from another input datafile.
"""
# initialize the parser
parser = argparse.ArgumentParser(description='Appends the input datafile with the toxgreen data from another input datafile')

# add the necessary arguments
parser.add_argument('-inFile','--inputFile', type=str, help='the input csv file')
parser.add_argument('-toxgreenFile','--toxgreenFile', type=str, help='the toxgreen csv file')
parser.add_argument('-outFile','--outputFile', type=str, help='the output csv file')
# add the optional arguments
parser.add_argument('-outDir','--outputDir', type=str, help='the output directory')

# extract the arguments into variables
args = parser.parse_args()
dataFile = args.inputFile
toxgreenFile = args.toxgreenFile
outputFile = args.outputFile
# default values for the optional arguments
outputDir = os.getcwd()
# if the optional arguments are not specified, use the default values
if args.outputDir is not None:
    outputDir = args.outputDir
    os.makedirs(outputDir, exist_ok=True)

if __name__ == '__main__':
    # check if dataFile exists
    if os.path.isfile(f'{outputDir}/{outputFile}.csv'):
        # quit
        print('DataFile', outputFile,'exists. To overwrite, delete the file and run again.')
        sys.exit()

    # read in the data files with interface column as string
    df = pd.read_csv(dataFile, dtype={'Interface': str})
    toxgreenDf = pd.read_csv(toxgreenFile)

    # get the columns of interest
    cols = ['Sequence','PercentGpA','PercentStd','Sample','toxgreen_fluor','toxgreen_std']
    # check if all the columns are present, otherwise only keep the ones that are present
    if all(col in toxgreenDf.columns for col in cols):
        toxgreenDf = toxgreenDf[cols]
    else:
        # get the columns that are present
        cols = [col for col in cols if col in toxgreenDf.columns]
        toxgreenDf = toxgreenDf[cols]

    # define the sequence column for the datafile
    df['Sequence'] = df['Geometry'].str[3:-5] # removes the first 3 and last 5 characters from the geometry column

    # append the matching sequence data from the toxgreen datafile to the input datafile
    df = df.merge(toxgreenDf, on='Sequence', how='left')

    # output the dataframe to a csv file
    df.to_csv(f'{outputDir}/{outputFile}.csv', sep=',', index=False)