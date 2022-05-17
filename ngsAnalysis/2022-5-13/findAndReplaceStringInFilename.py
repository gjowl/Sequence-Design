# @Author: Gilbert Loiseau
# @Date:   2022/04/10
# @Filename: findAndReplaceStringInFilename.py
# @Last modified by:   Gilbert Loiseau
# @Last modified time: 2022/04/10

"""
I made this script to run through filenames of music samples I downloaded online
and rename them. It takes a string, searches for it in every filename found within a
list of directories, and renames any file with that string to not having the string.

Using it to change filenames in my data directory
"""

import os
import sys

from pip import main
from stringFunctions import *

#TODO: make it so you can run this multiple times with multiple changes
if __name__ == '__main__':
    stringToRemove = sys.argv[1]
    stringToReplace = sys.argv[2]
    dirPath = sys.argv[3]
    replaceStringInName(stringToRemove, stringToReplace, dirPath)
