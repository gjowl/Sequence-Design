# @Author: Gilbert Loiseau
# @Date:   2022/04/10
# @Filename: findAndReplaceStringInFilename.py
# @Last modified by:   Gilbert Loiseau
# @Last modified time: 2022/04/10

"""
I made this script to run through filenames of music samples I downloaded online
and rename them. It takes a string, searches for it in every filename found within a
list of directories, and renames any file with that string to not having the string.
"""

import os

def replaceStringInFilename(string, mainDir):
    dirList = os.listdir(mainDir)
    for dir in dirList:
        fileDir = mainDir + dir
        try:
            fileList = os.listdir(fileDir)
            print(fileList)
            for file in fileList:
                oldFilename = fileDir + '/' + file
                if string in file:
                    newFilename = fileDir + '/' + file.strip(string)
                    os.rename(oldFilename, newFilename)
                    #TODO: write in a way to keep the old file names in case I don't like the new change
        except(FileNotFoundError):
            continue
        except(NotADirectoryError):
            continue

if __name__ == '__main__':
    stringToRemove = 'Orchid '
    dirPath = 'C:/Music Production/My Samples/Cymatics/Orchid/'
    replaceStringInFilename(stringToRemove, dirPath)
