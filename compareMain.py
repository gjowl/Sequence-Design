import os, sys, pandas as pd, argparse

# initialize the parser
parser = argparse.ArgumentParser(description='Compare the percentage of GpA in the sequence files')
parser.add_argument('-seqFile','--sequenceFile', type=str, help='the input file of sequences to be analyzed')
parser.add_argument('-inputDir','--inputDir', type=str, help='the input directory')

# extract the arguments into variables
args = parser.parse_args()
sequenceFile = args.sequenceFile
inputDir = args.inputDir

if __name__ == "__main__":
    cwd = os.getcwd()
    # loop through the directories in the inputDir
    for outerDir in os.listdir(inputDir):
        dirPath = f'{cwd}/{inputDir}/{outerDir}'
        # check if the directory is a directory
        if dirPath.endswith('.csv'):
            continue
        # loop through the directories in the directory
        for innerDir in os.listdir(dirPath):
            innerDirPath = f'{dirPath}/{innerDir}'
            # check if the directory is a directory
            if innerDirPath.endswith('.csv'):
                continue
            designFile = f'{innerDirPath}/aaPairsSeqs.csv'
            # execute the compareAaPercentages.py script
            execCompareAaPercentages = f'python3 compareAaPercentages.py -seqFile {cwd}/{sequenceFile} -designFile {designFile} -outputDir {innerDirPath}'
            print(execCompareAaPercentages)
            os.system(execCompareAaPercentages)
