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
#    Usage: python3 untarNGSFiles.py <ngsDir> <outputDir>
#    ngsDir: the directory containing the gzipped NGS files
#    outputDir: the directory to output the untarred files
#"""

import os, sys

# get the command line arguments
ngsDir = sys.argv[1]
outputDir = sys.argv[2]

# make the output directory if it doesn't exist
os.makedirs(outputDir, exist_ok=True)
# make output directories for fwd and rvs
fwdDir = f'{outputDir}/fwd'
rvsDir = f'{outputDir}/rvs'
os.makedirs(fwdDir, exist_ok=True)
os.makedirs(rvsDir, exist_ok=True)

# get the list of files in the directory
files = os.listdir(ngsDir)

# loop through the files
for f in files:
    # check if the file is a gz file
    if f[-3:] == '.gz':
        # get the file name
        name = f[:-3]
        # untar the file
        print(f'Untarring {f}...')
        os.system(f'gzip -dk {ngsDir}/{f}')
        # check if fwd or rvs
        if 'R1' in name:
            # move the file to the fwd output directory
            cmd = f'mv {ngsDir}/{name} {fwdDir}/{name}'
            os.system(cmd)
        else:
            cmd = f'mv {ngsDir}/{name} {rvsDir}/{name}'
            os.system(cmd)