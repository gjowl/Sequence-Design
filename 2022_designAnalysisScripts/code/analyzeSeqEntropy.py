import sys
import pandas as pd
import os

"""
    Compiles energyFile.csv files from an input directory and organizes for sequence entropy
"""

# get the path to the current directory
currentDir = os.getcwd()

# get the current working directory
cwd = os.getcwd()+"/"

# define the search directory
searchDir = sys.argv[1]

# define the output dataframe
outputDf = pd.DataFrame()

# get the parent directory
parentDir = os.path.dirname(searchDir)
# get the parent directory name
parentDirName = os.path.basename(parentDir)

# runNumber and seqEntropy file
seqEntropyComparisonDf = pd.read_csv(cwd+"seqEntropyComparison.csv",sep=',',header=0)

# for each directory in the search directory
for dir in os.listdir(searchDir):
    # loop through the files in the directory
    # check if the directory is a directory
    if os.path.isdir(searchDir+dir):
        for file in os.listdir(searchDir+dir):
            currDir = searchDir+dir+'/'
            # get the design number
            designNumber = dir.split('_')[1]
            # check filename
            if file == "energyFile.csv":
                filename = currDir+file
                # read the csv file into a dataframe
                header = pd.read_csv(filename,sep='\t',header=None, nrows=1)
                df = pd.read_csv(filename, sep='\t', header=None, skiprows=1)
                df.columns = header.iloc[0]
                # add the directory name to the dataframe
                df['Directory'] = dir
                df['DesignNumber'] = designNumber
                # combine the dataframes
                outputDf = pd.concat([outputDf,df],axis=0)

# remove the first column
# sort the dataframe by the Total
outputDf = outputDf.sort_values(by=['Total'])
# loop through unique seqEnbtropy values ion the seqEntropyComparisonDf
for seqEntropy in seqEntropyComparisonDf["seqEntropy"].unique():
    # get all the rows with the seqEntropy value
    seqEntropyDf = seqEntropyComparisonDf[seqEntropyComparisonDf['seqEntropy'] == seqEntropy]
    # loop through the seqEntropyDf design numbers
    designDf = pd.DataFrame()
    for designNumber in seqEntropyDf['designNumber']:
        # convert the design number to a string
        designNumber = str(designNumber)
        # get data from outputDf that matches the design number
        tmpDf = outputDf[outputDf['DesignNumber'] == designNumber]
        # keep only the rows with the design number, append using concat
        designDf = pd.concat([designDf,outputDf[outputDf['DesignNumber'] == designNumber]],axis=0)
    # sort the designDf by the Total
    designDf = designDf.sort_values(by=['Total'])
    # output the first Total and sequence
    print("seqEntropy: ",seqEntropy,"; Total: ",designDf.iloc[0]['Total'],"; Sequence: ",designDf.iloc[0]['Sequence'], "; DesignNumber: ",designDf.iloc[0]['DesignNumber'])
    print("NumDesigns less than -20: ",len(designDf[designDf['Total'] < -20]))
    # output the dataframe to a csv file as sequence entropy
    designDf.to_csv(cwd+"seqEntropy_"+str(seqEntropy)+".csv",sep='\t',index=False)
