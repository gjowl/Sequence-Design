import sys, os, pandas as pd

# get input directory from command line
inputDir = sys.argv[1]
outputFile = sys.argv[2] # csv file for running calcPdbEnergy script on condor

# get the name of the input directory without the path
inputDirName = os.path.basename(inputDir)

# initialize the outputDf
outputDf = pd.DataFrame(columns=['outputDir', 'pdb'])
# loop through all directories in the input directory
for dir in os.listdir(inputDir):
    # loop through all files in the directory
    i = 0
    for file in os.listdir(f'{inputDir}/{dir}'):
        # get the files with the .pdb extension that contain 'prepacked'
        if file.endswith('.pdb') and 'prepacked' in file:
            # add the pdb file and the output directory to the outputDf using concat
            outputDf = pd.concat([outputDf, pd.DataFrame({'outputDir': [dir+"_"+str(i)], 'pdb': [file]})])
            i += 1

# write the outputDf to a csv file
outputDf.to_csv(outputFile, index=False)