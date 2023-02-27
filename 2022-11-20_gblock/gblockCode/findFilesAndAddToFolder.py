import os, sys, pandas as pd

"""
 This program takes an input data file and a directory to search through.
 It then searches through the directory for files that match the filenames in the filenames column in the input data file.
 It then creates copies of those files to a given output directory name.
"""
# get the current working directory
cwd = os.getcwd()

# get the data file
dataFile = sys.argv[1]
# get the directory to search
searchDir = sys.argv[2]
# get the output directory
outputDir = sys.argv[3]

# load the data file into a pandas dataframe
data = pd.read_csv(dataFile, header=0)

# get the filename column
filenameCol = data["Filename"]

outputDir = cwd + '/' + outputDir
# make the output directory if it doesn't exist
if not os.path.exists(outputDir):
    os.system('mkdir ' + outputDir)

# search through the input directory for files within the directories in the input directory
for root, dirs, files in os.walk(searchDir):
    # search through the directories in the input directory
    for dir in dirs:
        # search through the files in the dir
        for file in os.listdir(f'{searchDir}{dir}'):
            # separate the file name from the extension
            if file in filenameCol.values:
                # copy the file to the current working directory
                os.system(f'cp {searchDir}{dir}/{file} {outputDir}')