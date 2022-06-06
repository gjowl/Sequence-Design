"""
This file is made to hold functions for my scripts that deal with string manipulation for my music related scripts
"""

import os
import pandas as pd

def replaceStringInName(oldString, newString, mainDir):
    dfFilenames = pd.DataFrame()
    prevFilenameList = []
    newFilenameList = []
    try:
        fileList = os.listdir(mainDir)
        for filename in fileList:
            if oldString in filename:
                newFilename = filename.replace(oldString, newString)
                print("old:", filename, oldString)
                print("new:", newFilename, newString)
                filename = mainDir + filename
                newFilename = mainDir + newFilename
                print("old:", filename, oldString)
                print("new:", newFilename, newString)
                os.rename(filename, newFilename)
                prevFilenameList.append(filename)
                newFilenameList.append(newFilename)
                #TODO: print new file names and ask if okay; otherwise, raise exception and undo
                #TODO: I think making classes makes the most sense, so I'm going to do that (actually might not be best, try thinking of somethign else)
                #https://www.youtube.com/watch?v=FM71_a3txTo&ab_channel=ArjanCodes
                # https://blender.stackexchange.com/questions/7066/python-undo-script-if-script-fails#:~:text=Wrap%20your%20script%20in%20an%20operator.%20You%20will,from%20Text%20Editor%20-%3E%20Python%20-%3E%20Operator%20Simple
        dfFilenames.insert(0, "Previous", prevFilenameList)
        dfFilenames.insert(1, "New", newFilenameList)
        dfFilenames.to_csv(mainDir+"revertFilenames.csv")
        # I screwed up renaming some; need to fix this reversion stuff; lost the reversion file, so redo gzip on LB0 and 12 tomorrow
    except(FileNotFoundError):
        exit('File not found')
    except(NotADirectoryError):
        exit('Not a directory')
