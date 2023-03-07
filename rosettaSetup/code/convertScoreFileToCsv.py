import os, sys, pandas as pd

# read input file from command line
inputFile = sys.argv[1]
outputDir = sys.argv[2]

# get the name of the input file without the path and extension
inputFileName = os.path.splitext(os.path.basename(inputFile))[0]

# read the input file line by line
df = pd.DataFrame()
with open(inputFile, 'r') as f:
    lines = f.readlines()
    # get the first line
    firstLine = lines[0]
    # separate the first line into a list separated by empty spaces
    firstLineList = firstLine.split()
    # add the firstLineList to a dataframe as the header
    df = pd.DataFrame(columns=firstLineList)
    # add the rest of the lines to the dataframe
    for line in lines[1:]:
        # separate the line into a list separated by empty spaces
        lineList = line.split()
        # add the lineList to the dataframe using concat
        df = pd.concat([df, pd.DataFrame([lineList], columns=firstLineList)], ignore_index=True)

# rid of the first column
df = df.drop(columns=['SCORE:'])
# convert all columns except last column to float
df[df.columns[:-1]] = df[df.columns[:-1]].astype(float)
# sort the dataframe by the rms column
df = df.sort_values(by=['rms'])
# save the dataframe as a csv file
df.to_csv(f'{outputDir}/{inputFile}.csv', index=False)