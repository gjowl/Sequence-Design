import sys, os, pandas as pd

# get input directory from command line
inputDir = sys.argv[1]
outputDir = sys.argv[2]

# get the name of the input directory without the path
inputDirName = os.path.basename(inputDir)

# initialize the dataframe
df = pd.DataFrame(columns=['protein', 'initialPdb', 'changedNamePdb'])

# loop through all directories in the input directory
for dir in os.listdir(inputDir):
    # loop through all files in the directory
    fileNumber = 0
    for file in os.listdir(f'{inputDir}/{dir}'):
        # get the files with the .pdb extension that contain 'prepacked'
        if file.endswith('.pdb') and 'prepacked' in file:
            # copy the file to the output directory
            copy = f'cp {inputDir}/{dir}/{file} {outputDir}/{dir}_{fileNumber}.pdb'
            os.system(copy)
            # add to the dataframe using concat
            df = pd.concat([df, pd.DataFrame([[dir, file, f'{dir}_{fileNumber}.pdb']], columns=['protein', 'initialPdb', 'changedNamePdb'])])
            fileNumber += 1

# save the dataframe to a csv file
df.to_csv(f'{outputDir}/pdbFileNames.csv', index=False)
print('pdb files put in ', outputDir)