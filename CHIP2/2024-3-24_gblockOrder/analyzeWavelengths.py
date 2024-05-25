'''
This file runs analysis for TOXGREEN data. The analysis includes:
    - merging the label file with the TOXGREEN data
    - normalizing the data to the NoTM row
    - calculating the percent Gpa
    - plotting the data at 512 nm as a bar graph
    - outputting the data to a csv file
    - the output directory is optional, if not given, the current working directory is used
    - the label file and TOXGREEN data are required

Run as: python3 analyzeToxgreen.py -labelFile labelFile.csv -toxgreenFile toxgreenData.csv -outputDir outputDirectory
'''

import os, sys, argparse, pandas as pd, numpy as np, matplotlib.pyplot as plt

# Parse command line arguments
parser = argparse.ArgumentParser(description='Analyze Toxgreen data')

# add the necessary arguments
parser.add_argument('-outputDir','--outputDir', type=str, help='the output directory')
parser.add_argument('-goodSamples','--goodSamples', type=str, help='the positive samples')
parser.add_argument('-badSamples','--badSamples', type=str, help='the negative samples')

# extract the arguments into variables
args = parser.parse_args()
outputDir = os.getcwd()
goodSamples = args.goodSamples
badSamples = args.badSamples
if args.outputDir is not None:
    outputDir = args.outputDir
os.makedirs(outputDir, exist_ok=True)

# plotting function
def plotData(averageData, replicateData, outputDir, outputName):
    fig, ax = plt.subplots()
    averageData.plot(kind='bar', x='Sample Name', y='Average Percent GpA', yerr='Standard Deviation', ax=ax, color='gray', edgecolor='black', capsize=5, width=0.8)
    for i in range(len(averageData['Sample Name'].unique())):
        sample = averageData['Sample Name'].unique()[i]
        sampleData = replicateData[replicateData['Sample Name'] == sample]
        # plot the data with a small open black circle in front of the bar
        ax.scatter([i] * len(sampleData), sampleData['Percent GpA'], color='white', s=10, marker='o', edgecolor='black')
        #ax.plot([i]*len(sampleData), sampleData['Percent GpA'], 'ko', markersize=2)
    # bring the data points to the front
    ax.set_zorder(1)
    plt.xlabel('Sample Name')
    plt.xticks(rotation=90)
    plt.ylabel('Percent GpA')
    plt.title('Percent GpA')
    plt.tight_layout()
    plt.savefig(f'{outputDir}/{outputName}.png')
    plt.savefig(f'{outputDir}/{outputName}.svg')

# main code
if __name__ == '__main__':
    # create a dataframe to store the wavelength data
    allReplicateData = pd.DataFrame()
    allWvlData = pd.DataFrame()
    # loop through all directories within the current directory that contain 'toxgreen'
    for root, dirs, files in os.walk(os.getcwd()):
        for dir in dirs:
            if 'toxgreen' in dir:
                toxgreenDir = f'{root}/{dir}'
                # read in the data
                wavelengthFile = pd.read_csv(f'{toxgreenDir}/wavelengthData.csv')
                # subtract the NoTM row from the data for each replicate
                noTM = wavelengthFile[wavelengthFile['Sample Name'] == 'NoTM']
                wavelengthData = pd.DataFrame()
                for replicate in wavelengthFile['Replicate'].unique():
                    replicateData = wavelengthFile[wavelengthFile['Replicate'] == replicate]
                    noTMReplicate = noTM[noTM['Replicate'] == replicate]
                    for sample in replicateData['Sample Name'].unique():
                        sampleData = replicateData[replicateData['Sample Name'] == sample]
                        sampleData['Absorbance'] = sampleData['Absorbance'] - noTMReplicate['Absorbance'].values[0]
                        wavelengthData = pd.concat([wavelengthData, sampleData], ignore_index=True)
                gpaData = wavelengthData[wavelengthData['Sample Name'] == 'Gpa']
                # get the average Absorbance for GpA
                gpaVal = gpaData['Absorbance'].mean()
                # add the toxgreenDir to the data
                wavelengthData['Toxgreen Dir'] = toxgreenDir
                allWvlData = pd.concat([allWvlData, wavelengthData], ignore_index=True)
                for replicate in gpaData['Replicate'].unique():
                    # calculate the percent GpA for each sample
                    replicateData = wavelengthData[wavelengthData['Replicate'] == replicate]
                    replicateData['Percent GpA'] = replicateData['Absorbance'] / gpaVal * 100
                    # average the data for each sample
                    #replicateData = replicateData.groupby('Sample Name').mean()
                    #replicateData.reset_index(inplace=True)
                    # replace the replicate number with the sample name
                    replicateData['Day'] = dir
                    allReplicateData = pd.concat([allReplicateData, replicateData], ignore_index=True)       
                # append the data to the wavelengthData dataframe
                #wavelengthData = pd.concat([wavelengthData, wavelengthFile], ignore_index=True)
    allWvlData.to_csv(f'{outputDir}/allData.csv', index=False)
    allReplicateData.to_csv(f'{outputDir}/allReplicateData.csv', index=False)

    replicateData = allReplicateData.copy()
    # transpose the data so that the replicates are columns
    # for each row, combine the day and replicate number into a single column
    replicateData['ReplicateDay'] = replicateData['Day'] + '-' + replicateData['Replicate'].astype(str)
    transposeData = replicateData.pivot(index='Sample Name', columns='ReplicateDay', values='Percent GpA')
    transposeData.reset_index(inplace=True)
    transposeData.to_csv(f'{outputDir}/transposedReplicateData.csv', index=False)
    # get the standard deviation of the data
    stdData = replicateData.groupby(['Sample Name', 'Day']).std()
    stdData.reset_index(inplace=True)
    stdData.rename(columns={'Percent GpA': 'Standard Deviation'}, inplace=True)
    stdData.rename(columns={'Absorbance': 'Absorbance-SD'}, inplace=True)
    # only keep the standard deviation, sample name, and day
    stdData = stdData[['Sample Name', 'Day', 'Standard Deviation', 'Absorbance-SD']]
    stdData.to_csv(f'{outputDir}/stdData.csv', index=False)

    # get the average percent GpA for each sample for each replicate
    allReplicateData = allReplicateData.groupby(['Sample Name', 'Day']).mean()
    allReplicateData.reset_index(inplace=True)
    allReplicateData.rename(columns={'Absorbance': 'Average Absorbance'}, inplace=True)
    # merge the standard deviation data with the average data
    allReplicateData = pd.merge(allReplicateData, stdData, on=['Sample Name', 'Day'], how='inner')
    # remove any data where the standard deviation is high (> 25)
    allReplicateData = allReplicateData[allReplicateData['Standard Deviation'] < 25]

    bestReplicateData = pd.DataFrame()
    # I repeated some more than twice to see if there was something wrong with the data from one day, and keep the data that is consistent between two days
    # remove data for replicates that have very different values
    for sample in allReplicateData['Sample Name'].unique():
        sampleData = allReplicateData[allReplicateData['Sample Name'] == sample]
        # check the difference between the two highest and two lowest values
        sampleData = sampleData.sort_values('Percent GpA')
        sampleData['Absorbance Diff'] = sampleData['Percent GpA'].diff()
        sampleData = sampleData.sort_values('Absorbance Diff', ascending=False)
        sampleData.drop(columns='Absorbance Diff', inplace=True)
        # keep the values with the lowest difference
        sampleData = sampleData.iloc[:2]
        ## keep only the 2 replicates with the most similar values
        #sampleData = sampleData[sampleData['Average Absorbance'] < sampleData['Average Absorbance'].mean() + sampleData['Average Absorbance'].std()]
        #sampleData = sampleData[sampleData['Average Absorbance'] > sampleData['Average Absorbance'].mean() - sampleData['Average Absorbance'].std()]
        ## check if there are 2 replicates left
        #if len(sampleData) != 2:
        #    # remove the replicate with the value that is the farthest from the mean
        #    sampleData['Absorbance Diff'] = abs(sampleData['Average Absorbance'] - sampleData['Average Absorbance'].mean())
        #    sampleData = sampleData.sort_values('Absorbance Diff', ascending=False)
        #    sampleData = sampleData.iloc[1:]
        #    # remove the Absorbance Diff column
        #    sampleData.drop(columns='Absorbance Diff', inplace=True)
        bestReplicateData = pd.concat([bestReplicateData, sampleData], ignore_index=True)

    # remove any data where there is only a single sample
    bestReplicateData = bestReplicateData[bestReplicateData['Sample Name'].duplicated(keep=False)]
    bestReplicateData.to_csv(f'{outputDir}/bestReplicateData.csv', index=False)

    finalReplicateData = pd.DataFrame()
    # keep rows with matching both sample and day data
    for sample in bestReplicateData['Sample Name'].unique():
        sampleData = replicateData[replicateData['Sample Name'] == sample]
        # only keep the days from the bestReplicateData
        sampleData = sampleData[sampleData['Day'].isin(bestReplicateData[bestReplicateData['Sample Name'] == sample]['Day'].unique())]
        finalReplicateData = pd.concat([finalReplicateData, sampleData], ignore_index=True)
    finalReplicateData.to_csv(f'{outputDir}/finalReplicateData.csv', index=False)
    # get the average data for each sample
    finalAverageReplicateData = finalReplicateData.groupby(['Sample Name']).mean()
    finalAverageReplicateData.reset_index(inplace=True)
    finalAverageReplicateData.rename(columns={'Absorbance': 'Average Absorbance'}, inplace=True)
    finalAverageReplicateData.rename(columns={'Percent GpA': 'Average Percent GpA'}, inplace=True)
    # get the standard deviation of the data
    stdData = finalReplicateData.groupby(['Sample Name']).std()
    stdData.reset_index(inplace=True)
    stdData.rename(columns={'Percent GpA': 'Standard Deviation'}, inplace=True)
    stdData.rename(columns={'Absorbance': 'Absorbance-SD'}, inplace=True)
    # only keep the standard deviation, sample name, and day
    stdData = stdData[['Sample Name', 'Standard Deviation', 'Absorbance-SD']]
    # merge the standard deviation data with the average data
    finalAverageReplicateData = pd.merge(finalAverageReplicateData, stdData, on=['Sample Name'], how='inner')
    finalAverageReplicateData.to_csv(f'{outputDir}/finalAverageReplicateData.csv', index=False)
    
    goodSamples = pd.read_csv(goodSamples)
    badSamples = pd.read_csv(badSamples)
    # get the average data for the good samples by merging the good samples with the finalAverageReplicateData
    goodData = pd.merge(goodSamples, finalAverageReplicateData, on='Sample Name', how='inner')
    badData = pd.merge(badSamples, finalAverageReplicateData, on='Sample Name', how='inner')

    # plot the data
    plotData(goodData, finalReplicateData, outputDir, 'goodSamples')
    plotData(badData, finalReplicateData, outputDir, 'badSamples')
    plotData(finalAverageReplicateData, finalReplicateData, outputDir, 'allSamples')
