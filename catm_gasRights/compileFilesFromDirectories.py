import os, sys, pandas as pd, argparse

"""
    Compiles energyFile.csv files from an input directory
"""

# initialize the parser
parser = argparse.ArgumentParser(description='Compiles energyFile.csv files from an input directory')

# add the necessary arguments
parser.add_argument('-inDir','--inputDir', type=str, help='the input directory')
parser.add_argument('-outFile','--outputFile', type=str, help='the output csv file')
parser.add_argument('-outDir','--outputDir', type=str, help='the output directory')

# extract the arguments into variables
args = parser.parse_args()
rawDataDir = args.inputDir
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
    
    # define the output dataframe
    outputDf = pd.DataFrame()
    
    # get the parent directory
    parentDir = os.path.dirname(rawDataDir)
    # get the parent directory name
    parentDirName = os.path.basename(parentDir)
    
    # for each directory in the search directory
    for dir in os.listdir(rawDataDir):
        innerDir = f'{rawDataDir}/{dir}'
        # check if the directory is a directory
        if os.path.isdir(innerDir):
            currDir = innerDir
            for file in os.listdir(currDir):
                # check that filename ends in .txt
                if file.endswith('.txt'):
                    filename = f'{currDir}/{file}'
                    # define the lines to keep
                    linesToKeep = [0, 10, 11, 13, 15, 16]
                    # keep the lines
                    with open(filename, 'r') as f:
                        lines = f.readlines()
                        # separate the lines by spaces
                        lines = [line.split() for line in lines]
                        # keep the lines
                        lines = [line for i, line in enumerate(lines) if i in linesToKeep]
                        # make the first part of the line into a header and the second part into a value
                        header = [line[0] for line in lines]
                        value = [line[1] for line in lines]
                        # create a dataframe
                        df = pd.DataFrame(value, index=header)
                        # transpose the dataframe so the header is the column name
                        df = df.T
                        outputDf = pd.concat([outputDf,df],axis=0)
                    ## read the csv file into a dataframe
                    #header = pd.read_csv(filename,sep=',',header=None, nrows=1)
                    ## read csv with interface column as string 
                    ##df = pd.read_csv(filename, sep=',', header=None, skiprows=1, dtype={1: str})# sets the interface column as a string
                    #df = pd.read_csv(filename, sep=',', header=None, skiprows=1)
                    #df.columns = header.iloc[0]
                    ## add the directory name to the dataframe
                    #df['Directory'] = dir
                    ## remove NA columns
                    #df = df.dropna(axis=1, how='all')
                    ## fixes the issue with the column names between different versions of the energyFile.csv
                    ##df = fixColumnNames(df)
                    ## combine the dataframes
                    #outputDf = pd.concat([outputDf,df],axis=0)
    # sort the dataframe by the Total
    #outputDf = outputDf.sort_values(by=['Total'])
    # get rid of any empty columns
    outputDf = outputDf.dropna(axis=1, how='all')
    # output the dataframe to a csv file
    outputDf.to_csv(f'{outputDir}/{outputFile}.csv', sep=',', index=False)