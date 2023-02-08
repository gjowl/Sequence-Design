import os, sys, pandas as pd

# initializes an class object to hold the data file. Contains simple functions for ease of handling data
class df_handler:
    # constructor
    def __init__(self):
        # instance variable
        self.data = None
    
    def setData(self, dataFile):
        # read in the input data from the command line
        data = pd.read_csv(dataFile)
        # keep only the stats columns
        self.data = data
    
    # returns data with only the columns in colNames
    def extractDataColumns(self, colNames):
        return self.data[colNames]

    # divides the stats in col1 by the stats in col2 and saves the result in newColName to 3 significant figures
    def colDivision(self, col1, col2, newColName):
        self.data[newColName] = (self.data[col1] / self.data[col2]).round(2) 

    # multiplies the stats in col1 by the stats in col2 and saves the result in newColName
    def colMultiply(self, col1, col2, newColName):
        self.data[newColName] = self.data[col1] * self.data[col2].round(2)

    # sorts the data by the stats in colName and returns the top n players
    def sortData(self, colName, ascend=False):
        self.data = self.data.sort_values(by=[colName], ascending=ascend)

    # imposes a limit for a column in the dataframe (i.e. only keep players with more than 10 points per game)
    def imposeLimit(self, colName, limit):
        self.data = self.data[self.data[colName] > limit]

    # returns the dataframe
    def getData(self):
        return self.data

    # returns the top n players in the data 
    def topN(self, n):
        return self.data.head(n)

    # returns the bottom n players in the data 
    def bottomN(self, n):
        return self.data.tail(n)
    
    # returns the top n players in the data sorted by colName
    def topNBy(self, n, colName):
        return self.data.sort_values(by=[colName], ascending=False).head(n)
    
    # returns the bottom n players in the data sorted by colName
    def bottomNBy(self, n, colName):
        return self.data.sort_values(by=[colName], ascending=True).head(n)