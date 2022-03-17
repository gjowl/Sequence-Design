# @Author: Gilbert Loiseau
# @Date:   2021-12-24
# @Filename: compileOptimizationDataFiles.py
# @Last modified by:   Gilbert Loiseau
# @Last modified time: 2021-12-25

"""
This searches for all of the optimizationEnergyFile.csv contained anywhere within the starting directory.
It then compiles all of them into a file for analysis by optimizedBackboneAnalysis.csv
"""

import os
import pandas as pd

#Functions
def writeDataframeToNewSpreadsheet(df, outFile):
    df.to_csv(outFile, sep=',')
    print(outFile)

# Main
if __name__ == '__main__':
    currDir_path = os.path.dirname(os.path.realpath(__file__))

    outputDir = currDir_path + '/Analysis'
    outFile = outputDir + '/compiledOptimizedBackboneData.csv'

    # Dataframe to save the energy files into
    df = pd.DataFrame()
    # This searches for all files within a given folder from the current directory
    for root, dirs, files in os.walk(currDir_path):
        if root.endswith('backboneOptimization'):
            for name in files:
                if name.endswith(("optimizationEnergyFile", ".csv")):
                    filename = root + "/" + name
                    #In my original outputs, I used grep -r "Backbone Optimization:" to compile my data. I rid of those with the below
                    tmpDf = pd.read_csv(filename, sep="[:\t]", engine='python')
                    tmpDf.reset_index(drop=True, inplace=True)
                    df = df.append(tmpDf)

    writeDataframeToNewSpreadsheet(df, outFile)
