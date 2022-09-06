import pandas as pd
import sys

#Read in the data file
datafile = sys.argv[1]
data = pd.read_csv(datafile)

# keep only data with PercentGpa > 0.6
data = data[data['PercentGpa'] > 50]
# keep only data with EnergyScore < 0
data = data[data['EnergyScore'] < 0]

# get the GxxxG space data
# only keep values from xShift below 7.5 and crossingAngle between -30 and -50
gxxxgData = data.loc[(data['xShift'] < 7.5) & (data['crossingAngle'] > -50) & (data['crossingAngle'] < -30)]

# get the right handed nonGxxxG space data
# only keep values from xShift above 8 and below 9 and crossingAngle between -30 and -50
rhNonGxxxGData = data.loc[(data['xShift'] > 8) & (data['xShift'] <9) & (data['crossingAngle'] > -50) & (data['crossingAngle'] < -30)]

# get the left handed space data
# only keep values from xShift between 7.5 and 8.0 and crossingAngle between 25 and 45
lhNonGxxxGData = data.loc[(data['xShift'] > 8) & (data['xShift'] < 9) & (data['crossingAngle'] > 25) & (data['crossingAngle'] < 45)]

# print all data to a csv file in the same directory as the original data file
gxxxgData.to_csv(datafile[:-4] + '_gxxxg.csv')
rhNonGxxxGData.to_csv(datafile[:-4] + '_rhNonGxxxG.csv')
lhNonGxxxGData.to_csv(datafile[:-4] + '_lhNonGxxxG.csv')

# add dataframes to a list
dataframes = [gxxxgData, rhNonGxxxGData, lhNonGxxxGData]
dataframeNames = ['gxxxg', 'rhNonGxxxG', 'lhNonGxxxG']

# columns to take average and stdDev
cols = ['PercentGpa', 'xShift', 'crossingAngle', 'axialRotation', 'zShift', 'EnergyScore', 'VDWDiff', 'HBONDDiff', 'IMM1Diff']

# get average and standard deviation of each column for each region
outputDf = pd.DataFrame(columns=['Region', 'Column', 'Average', 'Standard Deviation','Region Upper','Region Lower','NumSequences'])
for col in cols:
    for df, dfName in zip(dataframes, dataframeNames):
        avg = df[col].mean()
        stdDev = df[col].std()
        numSeqs = len(df.index)
        # get region size
        upperBound = avg+stdDev
        lowerBound = avg-stdDev
        # add to output dataframe using concat
        outputDf = pd.concat([outputDf, pd.DataFrame([[dfName, col, avg, stdDev, upperBound, lowerBound, numSeqs]], columns=['Region', 'Column', 'Average', 'Standard Deviation','Region Upper','Region Lower','NumSequences'])])

# print outputDf to a csv file in the same directory as the original data file with no first column
outputDf.to_csv(datafile[:-4] + '_regionStats.csv', index=False)
