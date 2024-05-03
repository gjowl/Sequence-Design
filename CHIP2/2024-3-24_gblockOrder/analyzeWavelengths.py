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

# extract the arguments into variables
args = parser.parse_args()
outputDir = os.getcwd()
if args.outputDir is not None:
    outputDir = args.outputDir
os.makedirs(outputDir, exist_ok=True)

# main code
if __name__ == '__main__':

    # create a dataframe to store the wavelength data
    outputData = pd.DataFrame()
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
                allWvlData = pd.concat([allWvlData, wavelengthData], ignore_index=True)
                for replicate in gpaData['Replicate'].unique():
                    # calculate the percent GpA for each sample
                    replicateData = wavelengthData[wavelengthData['Replicate'] == replicate]
                    replicateData['Percent GpA'] = replicateData['Absorbance'] / gpaVal * 100
                    outputData = pd.concat([outputData, replicateData], ignore_index=True)       
                # append the data to the wavelengthData dataframe
                #wavelengthData = pd.concat([wavelengthData, wavelengthFile], ignore_index=True)
    allWvlData.to_csv(f'{outputDir}/allData.csv', index=False)
    outputData.to_csv(f'{outputDir}/outputData.csv', index=False)

    # get the average wavelength data for each sample
    averageWvlData = allWvlData.groupby('Sample Name').mean()
    averageWvlData.reset_index(inplace=True)
    averageWvlData.rename(columns={'Absorbance': 'Average Absorbance'}, inplace=True)
    averageWvlData.to_csv(f'{outputDir}/averageWvlData.csv', index=False)
    print(averageWvlData.head())
    # get the average percent GpA for each sample
    averageData = outputData.groupby('Sample Name').mean()
    averageData.reset_index(inplace=True)
    # get the standard deviation of the data
    stdData = allWvlData.groupby('Sample Name').std()
    stdData.reset_index(inplace=True)
    stdData.to_csv(f'{outputDir}/stdData.csv', index=False)
    # rename the column std
    stdData.rename(columns={'Absorbance': 'Standard Deviation'}, inplace=True)
    print(stdData.head())
    print(averageData.head())
    print(averageWvlData.head())

    # divide the standard deviation by the average data to get the percent standard deviation
    averageData['Percent StDev'] = stdData['Standard Deviation'] / averageWvlData['Absorbance'] * averageData['Percent GpA']

    # create a bar plot of the data at 512 nm
    plt.bar(averageData['Sample Name'], averageData['Percent GpA'], yerr=averageData['Percent StDev'])
    plt.xlabel('Wavelength')
    plt.ylabel('Absorbance')
    plt.title('Toxgreen data')
    plt.legend()
    plt.savefig(f'{outputDir}/toxgreenData.png')
    plt.savefig(f'{outputDir}/toxgreenData.svg')

    averageData.to_csv(f'{outputDir}/plotData.csv', index=False)

    ## define variables
    #wavelength = '512'
    #gpaCol = 'Gpa'
    #percentGpa = 'Percent GpA'
    #percentStd = 'Percent Standard Deviation'
    #labelCol = 'Sample'

    ## add the label to the toxgreen data
    #mergedData = pd.merge(labelData, toxgreenData, on='Well', how='inner')

    ## separate the sample name and replicate number
    #mergedData['Sample Name'] = mergedData[labelCol].str.split('-').str[0]
    #mergedData['Replicate'] = mergedData[labelCol].str.split('-').str[1]

    ## Combine the data by sample name with sample and wavelength as columns
    #wavelengthData = mergedData.melt(id_vars=['Sample Name', 'Replicate'], value_vars=['512'], var_name='Wavelength', value_name='Absorbance')
    #wavelengthData.to_csv(f'{outputDir}/wavelengthData.csv', index=False)
    
    ## average all the columns by sample name
    #averageData = mergedData.groupby('Sample Name').mean()

    ## get the NoTM row
    #noTM = averageData[averageData.index == 'NoTM']
    ## subtract the NoTM row from the data
    #noTM_subtract = averageData.sub(noTM.iloc[0])
    ## make the index a column
    #averageData.reset_index(inplace=True)
    #noTM_subtract.reset_index(inplace=True)

    ## Calculate the Percent GpA
    #gpaVal = noTM_subtract[noTM_subtract['Sample Name'] == gpaCol][wavelength].values[0]
    #noTM_subtract[percentGpa] = noTM_subtract[wavelength] / gpaVal * 100

    ## get the standard deviation of the data
    #stdData = mergedData.groupby('Sample Name').std()
    #stdData.reset_index(inplace=True)
    
    ## transform the data into a format that can be used for plotting
    #transformData = transform(stdData, averageData, noTM_subtract, wavelength, percentGpa, percentStd)
    ## output the data to a csv file
    ## add a NoTM subtracted column that subtracts the 512 nm value from the NoTM row
    #transformData['NoTM subtracted'] = transformData[wavelength] - transformData[transformData['Sample Name'] == 'NoTM'][wavelength].values[0]
    #transformData.to_csv(f'{outputDir}/transformData.csv', index=False)

    ## make a bar plot of the data at 512 nm
    ## remove any data where percentStd < 0
    #transformData = transformData[transformData[percentStd] > 0]
    #plt.bar(transformData['Sample Name'], transformData[percentGpa], yerr=transformData[percentStd])
    #plt.xlabel(labelCol)
    ## set the labels to a 45 degree angle
    #plt.xticks(rotation=45)
    #plt.ylabel(wavelength)
    #plt.title('Toxgreen data')
    #plt.savefig(f'{outputDir}/toxgreenData.png')
    #plt.savefig(f'{outputDir}/toxgreenData.svg')