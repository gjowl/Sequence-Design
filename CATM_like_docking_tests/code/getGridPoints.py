import os, sys, pandas as pd

# get the command line arguments
inputFile = sys.argv[1]
outputDir = sys.argv[2]
numGeoms  = int(sys.argv[3])

# get the input file name without the extension
inputFileName = os.path.splitext(os.path.basename(inputFile))[0]
print(f'Input file name: {inputFileName}')

# make the output directory if it doesn't exist
os.makedirs(outputDir, exist_ok=True)

# read in the data as a pandas dataframe
df = pd.read_csv(inputFile,header=0)

# randomly choose the desired number of geometries from the dataframe
output_df = df.sample(n=numGeoms)

# if negAngle is true, then multiply the crossing angle by -1
if output_df['negAngle'].iloc[0] == True:
    output_df['crossingAngle'] = output_df['crossingAngle'].apply(lambda x: x*-1 if x > 0 else x)
# if negRot is true, then multiply the axial rotation by -1
if output_df['negRot'].iloc[0] == True:
    output_df['axialRotation'] = output_df['axialRotation'].apply(lambda x: x*-1 if x > 0 else x)

# reorganize the columns into the below order
output_df = output_df[['index', 'axialRotation', 'crossingAngle', 'zShift', 'xShift']]

# write the output dataframe to a csv file separated by space
output_df.to_csv(f'{outputDir}/{inputFileName}_CATM.csv', index=False, sep=' ')