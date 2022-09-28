import sys
import os
import pandas as pd
from functions import *

# plot histogram of dataframe and column
def plotHist(df, column, outputDir, binList, title):
    # Plotting code below
    fig, ax = plt.subplots()
    # get the minimum and maximum values of the column
    ax.hist(df[column], weights=np.ones(len(df))/len(df), bins=binList, color='b')
    # set y axis to percent
    plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
    # set the y axis label
    plt.ylabel('Frequency')
    # set the x axis label
    plt.xlabel(title)
    # set the title
    plt.title(title+' histogram')
    # save the number of data points on the figure
    # get min and max of column
    min = df[column].min()
    plt.text(min-0.2, -0.05, 'n = '+str(len(df)))
    # save the figure
    plt.savefig(outputDir+"/histogram.png", bbox_inches='tight', dpi=150)
    plt.close()

# get the input directory
inputDir = sys.argv[1]

# get current working directory
cwd = os.getcwd() + "/"

# get the column names
cols = 'xShift,crossingAngle,axialRotation,zShift'.split(',')
# setup output dataframe
outputDf = pd.DataFrame(columns=cols)
# loop through the files in the input directory
for file in os.listdir(inputDir):
    # check to see if the file is a pdb file
    if file.endswith('.pdb'):
        # remove the .pdb extension
        file = file[:-4]
        # split file by "_"
        splitFile = file.split('_')
        # get xShift, crossingAngle, axialRotation, and zShift
        xShift, crossingAngle, axialRotation, zShift = splitFile[0], splitFile[1], splitFile[2], splitFile[3]
        # keep only numbers
        xShift = xShift.replace('x', '')
        crossingAngle = crossingAngle.replace('cross', '')
        axialRotation = axialRotation.replace('ax', '')
        zShift = zShift.replace('z', '')
        # convert to float
        xShift = float(xShift)
        crossingAngle = float(crossingAngle)
        axialRotation = float(axialRotation)
        zShift = float(zShift)
        print(xShift, crossingAngle, axialRotation, zShift)
        # add to a dataframe
        outputDf = pd.concat([outputDf, pd.DataFrame([[xShift, crossingAngle, axialRotation, zShift]], columns=cols)])

# bin data
binList = np.arange(6.5, 7.5, 0.1)
col = 'xShift'
plotHist(outputDf, col, cwd, binList, col)
