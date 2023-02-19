import sys, os

# get input directory from command line
inputDir = sys.argv[1]

# get the name of the input directory without the path
inputDirName = os.path.basename(inputDir)

# loop through all files in the input directory
for file in os.listdir(inputDir):
    # untar the file
    untar = f'tar -xvf {inputDir}/{file}'
    os.system(untar)

print('untar complete')