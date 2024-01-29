import os, sys, pandas as pd, numpy as np

# get percent change for LB and M9 sequences
def getMeanPercent(numReplicates, listHours, df, inputDir, outputDir):
    # loop through all hours collected during maltose test
    # initialize dataframe to hold the averages for each replicate
    dfAvg = pd.DataFrame()
    for hour in listHours:
        # loop through all replicates for this 
        dfHour = df.filter(like="-"+hour)
        # set all 0 values to 1
        dfHour = dfHour.replace(0, np.nan)
        # get a dataframe with numerators and denominators
        mean = dfHour.mean(axis=1)
        colLength = len(dfAvg.columns)
        dfAvg.insert(colLength, hour, mean)
    dfAvg = dfAvg.replace(np.nan, 0)
    # add in sequence column to first column, then convert to index
    return dfAvg

def calculatePercentDifference(dfLB, dfM9):
    # initialize dataframe to hold the percent differences averages
    dfDiff = pd.DataFrame()
    # loop through columns in LB dataframe
    for LBcol in dfLB.columns:
        LB = dfLB[LBcol]
        # to prevent dividing by 0, replace all 0 values with 1
        LB = LB.replace(0, 1)
        # loop through the columns in the M9 dataframe
        for M9col in dfM9.columns:
            M9 = dfM9[M9col]
            # to differentiate between LB having a sequence and M9 not having it
            M9 = M9.replace(0, 1000000)
            subtract = M9.subtract(LB)
            percentDiff = subtract.divide(LB)*100
            numColumns = len(dfDiff.columns)
            dfDiff.insert(numColumns, f'LB-{LBcol}_M9-{M9col}', percentDiff)
    #dfDiff = dfDiff.replace(np.nan, 0)
    return dfDiff

# read in the command line arguments
maltoseFile = sys.argv[1]
outputFile = sys.argv[2]

# get the current directory
cwd = os.getcwd()

# read in the maltose file
maltoseDf = pd.read_csv(maltoseFile)

# keep only the M9 columns and Sequence and Segment columns
m9Cols = [col for col in maltoseDf.columns if 'M9' in col]
seqCols = ['Sequence', 'Segment']
keepCols = seqCols + m9Cols
maltoseDf = maltoseDf[keepCols]

# get the first letter of the M9 columns
design_regions = [col[0] for col in m9Cols]
# keep only the unique letters
design_regions = list(set(design_regions))

#outputDfs = []
#for df, hourList in zip(list_df, list_of_hours):
#    outputDf = getMeanPercent(numReplicates, hourList, df, inputDir, outputDir)
#    outputDfs.append(outputDf)
#df_percentDiff = calculatePercentDifference(outputDfs[0], outputDfs[1])
#outputDfs.append(df_percentDiff)
#nameList = ['LBPercents.csv', 'M9Percents.csv', 'percentDifference.csv']
#for df, name in zip(outputDfs, nameList):
#    outputAnalysisDfToCsv(df, seqs, segments, outputDir, name)

# below is just maltose pure comparison
# loop through the M9 letters
outputDf = pd.DataFrame()
for region in design_regions:
    print(region)
    # get the columns for this region
    regionCols = [col for col in m9Cols if col[0] == region]
    regionCols = seqCols + regionCols
    regionDf = maltoseDf[regionCols]
    # loop through the columns for this region
    for col in regionDf.columns:
        if col in seqCols:
            continue
        # get the negative control sequences for this region
        neg_seqs = regionDf[regionDf['Segment'].str.contains('N')]
        # get the max value for the negative control sequences
        neg_max = neg_seqs[col].max()
        print(neg_seqs)
        # divide the column by the max value
        regionDf[f'{col}_negControlRatio'] = regionDf[col] / neg_max
    # change anything with inf to 100000
    regionDf = regionDf.replace(np.inf, 100000)
    print(regionDf)
    # keep sequences where every negControlRatio column is greater than 1
    regionDf = regionDf[regionDf.filter(like='negControlRatio').gt(1).all(1)]
    outputDf = pd.concat([outputDf, regionDf], axis=1)

# save the output dataframe to a csv file
outputDf.to_csv(f'{cwd}/{outputFile}.csv', index=False)




