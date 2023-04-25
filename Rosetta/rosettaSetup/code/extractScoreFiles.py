import os, sys, pandas as pd

"""
This script extracts the score files from the output directory and renames them to the directory name.
"""

# get the input directory from the command line
inputDir = sys.argv[1]
outputDir = sys.argv[2]



# if the output directory exists, quit
if os.path.exists(outputDir):
    print(f'{outputDir} already exists. Files have already been extracted, delete {outputDir} to extract again.')
    quit()
else:
    # make the output directory if it doesn't exist
    os.makedirs(outputDir, exist_ok=True)

# loop through the directories in the input directory
for directory in os.listdir(inputDir):
    # get the directory path
    directoryPath = os.path.join(inputDir, directory)
    # check if the directory is a directory
    if os.path.isdir(directoryPath):
        # loop through the files in the directory
        for file in os.listdir(directoryPath):
            # get the file path
            filePath = os.path.join(directoryPath, file)
            # check if the filename is 'docked.sc'
            if file == 'docked.sc':
                # get the new file name
                newFileName = f'{directory}.sc'
                # read in the score file as a dataframe
                #TODO: add a function to read in the score file as a dataframe
                # copy the file to the output directory
                os.system(f'cp {filePath} {outputDir}/{newFileName}')