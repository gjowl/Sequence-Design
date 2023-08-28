import os, sys

# read in the command line arguments
designDir = sys.argv[1]
outputDir = sys.argv[2]

os.makedirs(outputDir, exist_ok=True)

# loop through the design directory
for dir in os.listdir(designDir):
    # loop through the files in the directory
    for file in os.listdir(designDir + '/' + dir):
        # if the file is a pdb file
        if file.endswith('.pdb'):
            # check if the first character in the file name is a number
            if file[0].isdigit():
                # copy the file to the output directory
                os.system('cp ' + designDir + '/' + dir + '/' + file + ' ' + outputDir + '/' + file)
