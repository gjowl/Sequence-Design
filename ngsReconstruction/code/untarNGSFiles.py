#"""
#File: d:\github\Sequence-Design\ngsReconstruction\code\untarNGSFiles.py
#Project: d:\github\Sequence-Design\ngsReconstruction\code
#Created Date: Wednesday November 15th 2023
#Author: gjowl
#-----
#Last Modified: Wednesday November 15th 2023 11:55:17 am
#Modified By: gjowl
#-----
#Description:
#This script untars the NGS files from the gz version to the fastq version for use in NGSreconstruction.
#"""

import os, sys

# get the command line arguments
ngsDir = sys.argv[1]
outputDir = sys.argv[2]

# make the output directory if it doesn't exist
os.makedirs(outputDir, exist_ok=True)

# get the list of files in the directory
files = os.listdir(ngsDir)

# loop through the files
for f in files:
    # check if the file is a gz file
    if f[-3:] == '.gz':
        # get the file name
        name = f[:-3]
        # untar the file
        print(f)
        os.system('gzip -dk '+ngsDir+f)
        # rename the file
        #os.system('mv '+outputDir+'fastq/'+name+' '+outputDir+'fastq/'+name[:-3])