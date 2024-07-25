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
    for sample in stdData['Sample Name']:
        sampleStd = stdData[stdData['Sample Name'] == sample][wavelength].values[0]
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

    # average all the columns by sample name
    averageData = mergedData.groupby('Sample Name').mean()

    # get the NoTM row
    noTM = averageData[averageData.index == 'NoTM']
    # subtract the NoTM row from the data
    noTM_subtract = averageData.sub(noTM.iloc[0])
    # make the index a column
    averageData.reset_index(inplace=True)
    noTM_subtract.reset_index(inplace=True)
    print(noTM_subtract)

    # Calculate the Percent GpA
    gpaVal = noTM_subtract[noTM_subtract['Sample Name'] == gpaCol][wavelength].values[0]
    noTM_subtract[percentGpa] = noTM_subtract[wavelength] / gpaVal * 100

    # get the standard deviation of the data
    stdData = mergedData.groupby('Sample Name').std()
    stdData.reset_index(inplace=True)
    
    # transform the data into a format that can be used for plotting
    transformData = transform(stdData, averageData, noTM_subtract, wavelength, percentGpa, percentStd)

    # make a bar plot of the data at 512 nm
    print(transformData)
    plt.bar(transformData['Sample Name'], transformData[percentGpa], yerr=transformData[percentStd])
    plt.xlabel(labelCol)
    # set the labels to a 45 degree angle
    plt.xticks(rotation=45)
    plt.ylabel(wavelength)
    plt.title('Toxgreen data')
    plt.savefig(f'{outputDir}/toxgreenData.png')
    plt.savefig(f'{outputDir}/toxgreenData.svg')

    # output the data to a csv file
    transformData.to_csv(f'{outputDir}/transformData.csv', index=False)