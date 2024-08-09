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
    ## check if dataFile exists
    #if os.path.isfile(f'{outputDir}/{outputFile}.csv'):
    #    # quit
    #    print('DataFile', outputFile,'exists. To overwrite, delete the file and run again.')
    #    sys.exit()
    
    # define the output dataframe
    outputDf = pd.DataFrame()
    
    # get the parent directory
    parentDir = os.path.dirname(rawDataDir)
    # get the parent directory name
    parentDirName = os.path.basename(parentDir)
    
    # loop to extract energies
    for dir in os.listdir(rawDataDir):
        innerDir = f'{rawDataDir}/{dir}'
        # check if the directory is a directory
        if os.path.isdir(innerDir):
            currDir = innerDir
            for file in os.listdir(currDir):
                # check that filename ends in .energy
                if file.endswith('.energy'):
                    filename = f'{currDir}/{file}'
                    with open(filename, 'r') as f:
                        lines = f.readlines()
                        # separate the lines by spaces
                        lines = [line.split() for line in lines]
                        header = [line[0] for line in lines]
                        value = [line[1] for line in lines]
                        # create a dataframe
                        df = pd.DataFrame(value, index=header)
                        # transpose the dataframe so the header is the column name
                        df = df.T
                        # add all the columns together to get the total
                        # convert the values to floats
                        df = df.astype(float)
                        df['Total'] = df['CHARMM_IMM1'] + df['CHARMM_IMM1REF'] +df['CHARMM_VDW'] + df['SCWRL4_HBOND']
                        # check if the CHARMM_IMM1REF > 0
                        if df['CHARMM_IMM1REF'].values[0] > 0:
                            seqFile = file.split('.')[0]
                            # add the sequence to the dataframe
                            df['filename'] = seqFile
                            df['Sequence'] = seqFile.split('_')[0]
                            outputDf = pd.concat([outputDf,df],axis=0)
    energyDf = outputDf.copy()
    energyDf.to_csv(f'{outputDir}/{outputFile}_energies.csv', sep=',', index=False)
    outputDf = pd.DataFrame()
    # loop to extract geometries
    for dir in os.listdir(rawDataDir):
        innerDir = f'{rawDataDir}/{dir}'
        # check if the directory is a directory
        if os.path.isdir(innerDir):
            currDir = innerDir
            for file in os.listdir(currDir):
                # check that filename ends in .txt
                if file.endswith('.txt'):
                    filename = f'{currDir}/{file}'
                    with open(filename, 'r') as f:
                        # check that the filename is in the energyDf
                        if file.split('.')[0] not in energyDf['filename'].values:
                            continue
                        lines = f.readlines()
                        # separate the lines by spaces
                        lines = [line.split() for line in lines]
                        # make the first part of the line into a header and the second part into a value
                        header = [line[0] for line in lines]
                        value = [line[1] for line in lines]
                        # keep only the first 17 lines
                        header = header[:17]
                        value = value[:17]
                        # create a dataframe
                        df = pd.DataFrame(value, index=header)
                        # transpose the dataframe so the header is the column name
                        df = df.T
                        # get the sequence from the filename
                        seq = file.split('_')[0]
                        # add the filename to the dataframe
                        df['filename'] = file.split('.')[0]
                        outputDf = pd.concat([outputDf,df],axis=0)
    # combine the energy and geometry dataframes
    outputDf = pd.merge(energyDf, outputDf, on='filename')
    # get the sequence from the filename
    outputDf['Sequence'] = outputDf['filename'].str.split('_').str[0]
    # remove the RAS from the sequence
    outputDf['Sequence'] = outputDf['Sequence'].str.replace('RAS','')
    # output the dataframe to a csv file
    outputDf.to_csv(f'{outputDir}/{outputFile}_all.csv', sep=',', index=False)
    # get rid of any empty columns
    outputDf = outputDf.dropna(axis=1, how='all')
    # keep the best sequence for each sequence (lowest total energy)
    outputDf = outputDf.sort_values(by=['Total']).groupby('Sequence').first().reset_index()
    # output the dataframe to a csv file
    outputDf.to_csv(f'{outputDir}/{outputFile}.csv', sep=',', index=False)