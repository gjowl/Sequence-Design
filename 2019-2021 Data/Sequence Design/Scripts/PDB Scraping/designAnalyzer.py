#This script is meant to be used to analyze data from my designed proteins (copied from interhelicalCoordinatesAnalyzer.py to run through directories

#TODO:
#figure out the best order to do script:
#   1. find out how to convert output files properly to csvs for easier handling

import os
import pandas as pd
import datetime
import re
#import numpy as np

########################################################################
#                             FUNCTIONS
########################################################################

def getListOfDir(dirName):
    # create a list of file and sub directories 
    # names in the given directory 
    listOfDir = os.listdir(dirName)
    allDir = []
    # Iterate over all the entries
    for entry in listOfDir:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # Check if entry is a directory 
        if os.path.isdir(fullPath):
            allDir.append(fullPath)
                
    return allDir 

#checks for only "pair_" files
def checkFiles(dirName):
    # create a list of file and sub directories 
    # names in the given directory 
    listOfDir = os.listdir(dirName)
    # Iterate over all the entries
    for entry in listOfDir:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        if 'seq_summary' in fullPath:
            return True

    return False

def addSummaryFile(dirName):
    # create a list of file and sub directories 
    # names in the given directory 
    listOfDir = os.listdir(dirName)
    sumFile = ''
    # Iterate over all the entries
    for entry in listOfDir:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        if 'seq_summary' in fullPath:
            sumFile = fullPath

    return sumFile

def getListOfFiles(dirName):
    # create a list of file and sub directories 
    # names in the given directory 
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory 
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            allFiles.append(fullPath)
    return allFiles 

########################################################################
#             FIND PDBS WITH AT LEAST ONE INTERACTING PAIR
########################################################################
now = datetime.datetime.now()
year = '{:02d}'.format(now.year)
month = '{:02d}'.format(now.month)
day = '{:02d}'.format(now.day)
hour = '{:02d}'.format(now.hour)
minute = '{:02d}'.format(now.minute)


#if rerun is False:
#    date ='{}_{}_{}'.format(year, month, day)
#    cluster = input("Insert data cluster level in bc_## format: ")
#else:
#    date = input("Insert date in year_month_day format for what data you would like to rerun: ")
#    
#alldata = pd.DataFrame()

########################################################################
#                  CHECK WHICH DATABASE TO ANALYZE
########################################################################
proteinDir = "lsdesign_left"

print("Analyzing membrane protein database...")
dirName = '/data02/gloiseau/Sequence_Design_Project/vdwSequenceDesign/' + proteinDir +'/06_20_2020/'#TODO: hardcoded for testing
    
########################################################################
#         READ PAIR CSV FILES INTO DATAFRAME AND OUTPUT AS CSV
########################################################################
listOfDir = getListOfDir(dirName)
summaries = []
count = 0

for elem in listOfDir:
    if checkFiles(elem):
        summaries.append(addSummaryFile(elem))#TODO: then here change this to something that will delineate things into a csv properly (this is likely the hard part)
        count += 1
#TODO: add in a way to extract the design number from the directory here

designNeg = []
design = []
seq = []
xShift = []
crossAng = []
axialRot = []
zShift = []
monomer = []
dimer = []
final = []

dupSeqDesign = []
dsseq = []
dsxShift = []
dscrossAng = []
dsaxialRot = []
dszShift = []
dsmonomer = []
dsdimer = []
dsfinal = []

for summary in summaries:
    with open(summary, 'rt', encoding='latin-1') as inputfile:#not 100% sure what an encoding error is, but I was able to fix it with latin-1 encoding(I assume it is just the text style written in the file)
        for line in inputfile:
            if 'Final Energy: -' in line:
                designNeg.append(summary)#TODO: I think some of my files didn't have any sequences? figure out why this is the case; but for now, using this as temproary to determine design#
            else:
                continue

for summary in designNeg:
    with open(summary, 'rt', encoding='latin-1') as inputfile:#not 100% sure what an encoding error is, but I was able to fix it with latin-1 encoding(I assume it is just the text style written in the file)
        for line in inputfile:
            if 'Sequence' in line:
                l = line.split()
                if l[2] not in seq:
                    seq.append(l[2])
                    design.append(summary)#TODO: I think some of my files didn't have any sequences? figure out why this is the case; but for now, using this as temproary to determine design#
                else:
                    dsseq.append(l[2])
                    dupSeqDesign.append(summary)
            else:
                continue

for summary in design:
    with open(summary, 'rt', encoding='latin-1') as inputfile:#not 100% sure what an encoding error is, but I was able to fix it with latin-1 encoding(I assume it is just the text style written in the file)
        for i, line in enumerate(inputfile):
            if i > 6:
                if 'xShift' in line:
                    l = line.split()
                    xShift.append(l[1])
                elif 'cross' in line:
                    l = line.split()
                    crossAng.append(l[1])
                elif 'axial' in line:
                    l = line.split()
                    axialRot.append(l[1])
                elif 'zShift' in line:
                    l = line.split()
                    zShift.append(l[1])
                elif 'Monomer' in line:
                    l = line.split()
                    monomer.append(l[2])
                elif 'Dimer' in line:
                    l = line.split()
                    dimer.append(l[2])
                elif 'Final' in line:
                    l = line.split()
                    final.append(l[2])

            
for summary in dupSeqDesign:
    with open(summary, 'rt', encoding='latin-1') as inputfile:#not 100% sure what an encoding error is, but I was able to fix it with latin-1 encoding(I assume it is just the text style written in the file)
        for i, line in enumerate(inputfile):
            if i > 6:
                if 'xShift' in line:
                    l = line.split()
                    dsxShift.append(l[1])
                elif 'cross' in line:
                    l = line.split()
                    dscrossAng.append(l[1])
                elif 'axial' in line:
                    l = line.split()
                    dsaxialRot.append(l[1])
                elif 'zShift' in line:
                    l = line.split()
                    dszShift.append(l[1])
                elif 'Monomer' in line:
                    l = line.split()
                    dsmonomer.append(l[2])
                elif 'Dimer' in line:
                    l = line.split()
                    dsdimer.append(l[2])
                elif 'Final' in line:
                    l = line.split()
                    dsfinal.append(l[2])

########################################################################
#                     WRITE CSV FILE
########################################################################
data = pd.DataFrame()
print(len(design))
data["Design Path"] = design
data["Sequence"] = seq
#data["Start xShift"] = sgxShift
#data["Start crossingAngle"] = sgcrossAng
#data["Start axialRotation"] = sgaxialRot
#data["Start zShift"] = sgzShift
#TODO: haven't gotten it to work for the starting geometries yet (they're not adding to the array for some reason)
data["xShift"] = xShift
data["crossingAngle"] = crossAng 
data["axialRotation"] = axialRot
data["zShift"] = zShift
data["Monomer Energy"] = monomer 
data["Dimer Energy"] = dimer
data["Final Energy"] = final

dupSeqData = pd.DataFrame()
dupSeqData["Design Path"] = dupSeqDesign
dupSeqData["Sequence"] = dsseq
dupSeqData["xShift"] = dsxShift
dupSeqData["crossingAngle"] = dscrossAng 
dupSeqData["axialRotation"] = dsaxialRot
dupSeqData["zShift"] = dszShift
dupSeqData["Monomer Energy"] = dsmonomer 
dupSeqData["Dimer Energy"] = dsdimer
dupSeqData["Final Energy"] = dsfinal
#TODO: add in a way to extract the design number from the directory
########################################################################
#                     WRITE OUTPUT FILE AS CSV
########################################################################
#The above adds on an extra column right at the beginning

data.to_csv('/exports/home/gloiseau/designAnalysis.csv', sep='\t')
dupSeqData.to_csv('/exports/home/gloiseau/designAnalysis_duplicates.csv', sep='\t')
#TODO: pretty sure I can make multiple tabs; add that in here so then I only make one csv
#print("finished")

#with open(allPairs[0], 'r') as csvfile:
#    reader = csv.reader(csvfile, delimiter = '\t')
#    for row in reader:
#        print(row[17], row[19], row[23], row[24], row[30], row[31], row[36], row[37])

