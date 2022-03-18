# @Author: Gilbert Loiseau
# @Date:   2021-12-25
# @Filename: compileAllDesignEnergyFiles.py
# @Last modified by:   Gilbert Loiseau
# @Last modified time: 2021-12-25

"""
This searches for all of the energyFile.csv contained anywhere within the starting directory.
It then compiles all of them into a file for analysis by compiledDesignData.csv
"""

import os
import pandas as pd
import helper

#Functions
def writeDataframeToNewSpreadsheet(df, outFile):
    df.to_csv(outFile, sep=',')

programName = "compileDesignData"

# Main
if __name__ == '__main__':
    config = helper.read_config()

    outputDir = config[programName]["outputDir"]
    dataDir = config[programName]["dataDir"]
    outFile = outputDir + config[programName]["outFile"]

    # Dataframe to save the energy files into
    df = pd.DataFrame()
    #TODO: I think this works...but it's currently pulling in all of the optimization files too. try to fix that
    # This searches for all files within a given folder from the current directory
    for root, dirs, files in os.walk(dataDir):
        for name in files:
            if name.endswith(("energyFile", ".csv")):
                filename = root + "/" + name
                tmpDf = pd.read_csv(filename, sep="[:\t]", engine='python')
                #In my original outputs, I used grep -r "Sequence Info:" to compile my data. I rid of those with the below
                tmpDf.reset_index(drop=True, inplace=True)
                df = df.append(tmpDf)

    # Output dataframe of all the energyFiles
    writeDataframeToNewSpreadsheet(df, outFile)
