import os, sys, pandas as pd, argparse

# initialize the parser
parser = argparse.ArgumentParser(description='Create the backbone repack file for submitting to the cluster')

# add the necessary arguments
parser.add_argument('-inFile','--inputFile', type=str, help='the input file with the design data')
# add the optional arguments
parser.add_argument('-outDir','--outputDir', type=str, help='the output directory')

# extract the arguments into variables
args = parser.parse_args()
inputFile = args.inputFile
outputDir = os.getcwd()
# if the optional arguments are not specified, use the default values
if args.outputDir is not None:
    outputDir = args.outputDir

if __name__ == '__main__':
    # read in the input file
    df = pd.read_csv(inputFile)
    
    # make the output directory if it doesn't exist
    os.makedirs(outputDir, exist_ok=True)
    
    # get the necessary columns
    df = df[['Sequence', 'Interface', '', 'std_adjusted', 'toxgreen_fluor', 'toxgreen_std']]
    
    # save the dataframe to a csv file
    df.to_csv(f'{outputDir}/backboneRepacks.csv', index=False)
    print('backbone repack file created in ', outputDir)