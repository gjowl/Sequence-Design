import sys, os, pandas as pd

# get input directory from command line
inputDir = sys.argv[1]
outputFile = sys.argv[2] # csv file for running calcPdbEnergy script on condor

# get the name of the input directory without the path
inputDirName = os.path.basename(inputDir)

# initialize the outputDf
outputDf = pd.DataFrame(columns=['outputDir', 'pdb'])
# loop through all files in the input directory
for file in os.listdir(inputDir):
    # split the file name by the .
    filename = file.split('.')[0]
    # add the file to the outputDf
    outputDf = pd.concat([outputDf, pd.DataFrame([[filename, file]], columns=['outputDir', 'pdb'])])

# write the outputDf to a csv file
outputDf.to_csv(outputFile, index=False)