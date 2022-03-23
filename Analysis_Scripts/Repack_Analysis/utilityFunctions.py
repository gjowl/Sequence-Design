# @Author: Gilbert Loiseau
# @Date:   2021-11-11
# @Filename: utility.py
# @Last modified by:   Gilbert Loiseau
# @Last modified time: 2022/03/22

"""
Created on 11/11/21 18:37:30 2021

Description:
  -This is a python file that contains a host of useful utility functions that I wrote.

To add to your own python file, download this file to the same directory of your file.
Add the below to the top of the your file:
  -from utilityFunctions.py import *

You will then be able to use the commands from this file on your own.
"""

# Packages
import os
import pandas as pd

#This function iterates through a row of data and identifies whether or not the value in the column is a string
def getNumericColumns(allColumnNames, dataRow):
    #Array that the column names with numeric columns will be added to
    numColumnNames = []
    for i in range(len(dataRow)):
        val = dataRow[i]
        try:
            float(val)
            numColumnNames.append(allColumnNames[i])
        except ValueError:
            print(allColumnNames[i] + " is not a string column")
    return numColumnNames

# Add column names to dictionary
def addColumnsToDictionary(dict, colNames):
        for i in colNames:
            dict[i] = []

# Outputs a dictionary of means for a list of columns
def getColumnAverages(df, columnNames, dict):
    # Iterate through columns and collect means of data
    for i in range(len(columnNames)):
        currColumn = columnNames[i]
        dict[currColumn].append(df[currColumn].mean())

def writeDataframeToSpreadsheet(df, writer, sheetName):
    df.to_excel(writer, sheet_name=sheetName)

def writeDataframeToNewSpreadsheet(df, outFile, sheetName):
    writer = pd.ExcelWriter(outFile)
    df.to_excel(writer, sheet_name=sheetName)
    writer.save()
    writer.close()

def getRunTime(startTime):
    endTime = time.perf_counter()
    totalTime = endTime-startTime
    print(totalTime)
    return totalTime

#class noConfigException():
#    def __init__(self):
#        self.message = "No config file found! Make sure there is a <fileName>.config file found in the program directory"
#    def print_error(self):
#        print(self.message)
def getConfigFile():
    configFile = ''
    # Access the configuration file for this program (should only be one in the directory)
    programPath = os.path.realpath(__file__)
    programDir, programFile = os.path.split(programPath)
    programName, programExt = os.path.splitext(programFile)
    fileList = os.listdir(programDir)
    for file in fileList:
        fileName, fileExt = os.path.splitext(file)
        if fileExt == '.config':
            configFile = programDir + '/' + file
    if configFile == '':
        print("No config given! Break")
    return configFile
#try:
#    configFile = getConfigFile()
#except noConfigException as error:
#    print("Bad input : {configFile}")
#    print("{error.message}")
def makeOutputDir(outputDir)
    if not os.path.isdir(outputDir):
        print('Creating output directory: ' + outputDir + '.')
        os.mkdir(outputDir)
    else:
        print('Output Directory: ' + outputDir + ' exists.')
