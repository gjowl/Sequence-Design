import os, sys, pandas as pd, argparse

# initialize the parser
parser = argparse.ArgumentParser(description='Concatenates energyFile with experimental data')
# add the necessary arguments
parser.add_argument('-energyFile','--energyFile', type=str, help='the energyFile.csv file')
parser.add_argument('-expData','--experimentalData', type=str, help='the experimental data file')
# add the optional arguments
parser.add_argument('-outFile','--outputFile', type=str, help='the output csv file')
parser.add_argument('-outDir','--outputDir', type=str, help='the output directory')
# extract the arguments into variables
args = parser.parse_args()
energyFile = args.energyFile
expData = args.experimentalData
# default values for the optional arguments
outputFile = 'energyFile_expData'
outputDir = os.getcwd()
# if the optional arguments are not specified, use the default values
if args.outputFile is not None:
    outputFile = args.outputFile
if args.outputDir is not None:
    outputDir = args.outputDir
    os.makedirs(outputDir, exist_ok=True)

if __name__ == '__main__':
    # check if dataFile exists
    if os.path.isfile(f'{outputDir}/{outputFile}.csv'):
        # quit
        print('DataFile', outputFile,'exists. To overwrite, delete the file and run again.')
        sys.exit()
    
    # read the energyFile
    energyDf = pd.read_csv(energyFile)
    # read the experimental data
    expDf = pd.read_csv(expData)
    # get the columns of interest from the experimental data
    expDf = expDf[['Sequence', 'toxgreen_fluorescence', 'toxgreen_std', 'deltaG', 'deltaG_std']]
    # merge the dataframes
    outputDf = pd.merge(energyDf, expDf, on='Sequence')
    # write the output dataframe to a csv file
    outputDf.to_csv(f'{outputDir}/{outputFile}.csv', index=False)