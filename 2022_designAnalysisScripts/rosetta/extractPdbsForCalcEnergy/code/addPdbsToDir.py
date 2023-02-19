import sys, os

# get input directory from command line
inputDir = sys.argv[1]

# get the name of the input directory without the path
inputDirName = os.path.basename(inputDir)

# loop through all directories in the input directory
for dir in os.listdir(inputDir):
    # loop through all files in the directory
    for file in os.listdir(f'{inputDir}/{dir}'):
        # get the files with the .pdb extension
        if file.endswith('.pdb'):
            # copy the file to the output directory
            copy = f'cp {inputDir}/{dir}/{file} {outputDir}'
            os.system(copy)

print('pdb files put in ', outputDir)