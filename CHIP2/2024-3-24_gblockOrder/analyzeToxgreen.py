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
parser.add_argument('-labelFile','--labelFile', type=str, help='the input label file') 
parser.add_argument('-toxgreenFile','--toxgreenFile', type=str, help='the toxgreen data')
parser.add_argument('-outputDir','--outputDir', type=str, help='the output directory')

# extract the arguments into variables
args = parser.parse_args()
labelFile = args.labelFile
toxgreenFile = args.toxgreenFile
outputDir = os.getcwd()
if args.outputDir is not None:
    outputDir = args.outputDir
os.makedirs(outputDir, exist_ok=True)

# transform the data into a format that can be used for plotting
def transform(stdDevData, averageData, noTMData, wavelength, percentGpaCol, percentStdCol):
    outputDf = pd.DataFrame()
    for sample in stdDevData['Sample Name']:
        sampleStd = stdDevData[stdDevData['Sample Name'] == sample][wavelength].values[0]
        sampleVal = averageData[averageData['Sample Name'] == sample][wavelength].values[0]
        sampleGpa = noTMData[noTMData['Sample Name'] == sample][percentGpa].values[0]
        outputDf = outputDf.append({'Sample Name': sample, 'Standard Deviation': sampleStd, wavelength: sampleVal, percentGpaCol: sampleGpa, percentStdCol: (sampleStd / sampleVal) * sampleGpa}, ignore_index=True)
    return outputDf

# main code
if __name__ == '__main__':
    # read in the data
    labelData = pd.read_csv(labelFile)
    toxgreenData = pd.read_csv(toxgreenFile)

    # define variables
    wavelength = '512'
    gpaCol = 'Gpa'
    percentGpa = 'Percent GpA'
    percentStd = 'Percent Standard Deviation'
    labelCol = 'Sample'

    # add the label to the toxgreen data
    mergedData = pd.merge(labelData, toxgreenData, on='Well', how='inner')

    # separate the sample name and replicate number
    mergedData['Sample Name'] = mergedData[labelCol].str.split('-').str[0]
    mergedData['Replicate'] = mergedData[labelCol].str.split('-').str[1]

    # Combine the data by sample name with sample and wavelength as columns
    wavelengthData = mergedData.melt(id_vars=['Sample Name', 'Replicate'], value_vars=['512'], var_name='Wavelength', value_name='Absorbance')
    wavelengthData.to_csv(f'{outputDir}/wavelengthData.csv', index=False)
    
    # average all the columns by sample name
    averageData = mergedData.groupby('Sample Name').mean()

    # get the NoTM row
    noTM = averageData[averageData.index == 'NoTM']
    # subtract the NoTM row from the data
    noTM_subtract = averageData.sub(noTM.iloc[0])
    # make the index a column
    averageData.reset_index(inplace=True)
    noTM_subtract.reset_index(inplace=True)

    # Calculate the Percent GpA
    gpaVal = noTM_subtract[noTM_subtract['Sample Name'] == gpaCol][wavelength].values[0]
    noTM_subtract[percentGpa] = noTM_subtract[wavelength] / gpaVal * 100

    # get the standard deviation of the data
    stdData = mergedData.groupby('Sample Name').std()
    stdData.reset_index(inplace=True)
    
    # transform the data into a format that can be used for plotting
    transformData = transform(stdData, averageData, noTM_subtract, wavelength, percentGpa, percentStd)
    # output the data to a csv file
    # add a NoTM subtracted column that subtracts the 512 nm value from the NoTM row
    transformData['NoTM subtracted'] = transformData[wavelength] - transformData[transformData['Sample Name'] == 'NoTM'][wavelength].values[0]
    transformData.to_csv(f'{outputDir}/transformData.csv', index=False)

    # make a bar plot of the data at 512 nm
    # remove any data where percentStd < 0
    transformData = transformData[transformData[percentStd] > 0]
    plt.bar(transformData['Sample Name'], transformData[percentGpa], yerr=transformData[percentStd])
    plt.xlabel(labelCol)
    # set the labels to a 45 degree angle
    plt.xticks(rotation=45)
    plt.ylabel(wavelength)
    plt.title('Toxgreen data')
    plt.savefig(f'{outputDir}/toxgreenData.png')
    plt.savefig(f'{outputDir}/toxgreenData.svg')