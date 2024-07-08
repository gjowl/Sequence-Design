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

# a BS function that standardized the column names for the energyFile.csv files that have different column names (usually from different runs of the program after I changed a small thing in the code)
def fixColumnNames(input_df):
    # find _ in the column names and store them in a list
    colsWithUnderscore = input_df.columns[input_df.columns.str.contains('_')].tolist()
    # loop through the columns with _
    for col in colsWithUnderscore:
        # make sure the first letter after the _ is capitalized
        newName = col.split('_')[0] + col.split('_')[1].capitalize()
        # rename the column
        input_df.rename(columns={col:newName},inplace=True)
    # for any columns containing Shift, make sure the S is capitalized
    colsWithShift = input_df.columns[input_df.columns.str.contains('shift')].tolist()
    for col in colsWithShift:
        newName = col.replace('shift','Shift')
        input_df.rename(columns={col:newName},inplace=True)
    # for any columns containing angle, make sure the A is capitalized
    colsWithAngle = input_df.columns[input_df.columns.str.contains('angle')].tolist()
    for col in colsWithAngle:
        newName = col.replace('angle','Angle')
        input_df.rename(columns={col:newName},inplace=True)
    # for any columns containing rotation, make sure the R is capitalized
    colsWithRotation = input_df.columns[input_df.columns.str.contains('rotation')].tolist()
    for col in colsWithRotation:
        newName = col.replace('rotation','Rotation')
        input_df.rename(columns={col:newName},inplace=True)
    # for any columns with Dimer, remove
    colsWithDimer = input_df.columns[input_df.columns.str.contains('Dimer')].tolist()
    for col in colsWithDimer:
        newName = col.replace('Dimer','')
        input_df.rename(columns={col:newName},inplace=True)
    # capitalize the O in optimize
    colsWithOptimize = input_df.columns[input_df.columns.str.contains('optimize')].tolist()
    for col in colsWithOptimize:
        newName = col.replace('optimize','Optimize')
        input_df.rename(columns={col:newName},inplace=True)
    return input_df

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
            # loop through the files in the directory
            #for dir in os.listdir(innerDir):
            #    currDir = f'{innerDir}/{dir}/'
            for file in os.listdir(currDir):
                # check filename
                if file == "energyFile.csv":
                    filename = f'{currDir}/{file}'
                    #print(filename)
                    # read the csv file into a dataframe
                    header = pd.read_csv(filename,sep=',',header=None, nrows=1)
                    # read csv with interface column as string 
                    df = pd.read_csv(filename, sep=',', header=None, skiprows=1, dtype={1: str})# sets the interface column as a string
                    df.columns = header.iloc[0]
                    # add the directory name to the dataframe
                    df['Directory'] = dir
                    # remove NA columns
                    df = df.dropna(axis=1, how='all')
                    # fixes the issue with the column names between different versions of the energyFile.csv
                    df = fixColumnNames(df)
                    # combine the dataframes
                    outputDf = pd.concat([outputDf,df],axis=0)
    # sort the dataframe by the Total
    outputDf = outputDf.sort_values(by=['Total'])
    # get rid of any empty columns
    outputDf = outputDf.dropna(axis=1, how='all')
    # output the dataframe to a csv file
    outputDf.to_csv(f'{outputDir}/{outputFile}.csv', sep=',', index=False)