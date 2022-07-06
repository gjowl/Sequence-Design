import pandas as pd

class data(object):
    def __init__(self, df, name):
        self.df = df
        self.name = name

    def getDf(self):
        return self.df

    def getName(self):
        return self.name

    def compareColumns(self, col1, col2, name):
        df = self.df
        dfCc = df[df[col1] == df[col2]]
        dataCc = data(dfCc,name)
        return dataCc

    def getDuplicates(self, col, keepBool=False):
        df = self.df
        dfGd = df.duplicated(subset=col, keep=keepBool)
        dataGd = data(dfGd,"Duplicates")
        return dataGd
    
    def filterDuplicates(self, col, keepBool=False):
        df = self.df
        dfFd = df.drop_duplicates(subset=col, keep=keepBool)
        dataFd = data(dfFd,"No Duplicates")
        return dataFd
