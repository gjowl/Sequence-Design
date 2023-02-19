import sys

# get input directory from command line
inputDir = sys.argv[1]
csvFile = sys.argv[2] # csv file that contains the 

# get the name of the input directory without the path
inputDirName = os.path.basename(inputDir)

# initialize the outputDf
outputDf = pd.DataFrame(columns=['pdb', 'outputDir'])
# loop through all directories in the input directory
for dir in os.listdir(inputDir):
    # loop through all files in the directory
    for file in os.listdir(f'{inputDir}/{dir}'):
        # get the files with the .pdb extension
        if file.endswith('.pdb'):
            # add the pdb file and the output directory to the outputDf using concat
            outputDf = pd.concat([outputDf, pd.DataFrame({'pdb': [file], 'outputDir': [dir]})])

# write the outputDf to a csv file
outputDf.to_csv(csvFile, index=False)