import os, sys

# read in the pdb file from command line
pdbFileDir = sys.argv[1]
outputDir = sys.argv[2]

# create the output directory
os.makedirs(name=outputDir, exist_ok=True)

# loop through the pdb files
for pdbFile in os.listdir(pdbFileDir):
    # get the name of the pdb file
    pdbName = os.path.basename(pdbFile)
    # delete the first 3 lines of the pdb file
    inputFile = f'{pdbFileDir}/{pdbFile}'
    outputFile = f'{outputDir}/{pdbName}'
    with open(inputFile, 'r') as old, open(outputFile, 'w') as new:
        lines = old.readlines()
        # find the line that matches HETATM
        endLine = 0
        for i in range(len(lines)):
            if lines[i].startswith('HETATM'):
                endLine = i
                break
        new.writelines(lines[9:endLine])
        old.close()
        new.close()
