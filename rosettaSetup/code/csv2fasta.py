#This program will take a csv of the form: sequence,name and output a fasta file for each sequence to your specified directory 
# as well as write a csv called 'sequenceFiles.csv' of the form: fasta file,name
#Usage: python3 csv2fasta.py input.csv

import sys
import csv
import os

# get the current directory
currentDir = os.getcwd()
outputDir = currentDir+'/fastaFiles'

# make the output directory if it doesn't exist
if not os.path.exists(outputDir):
    os.makedirs(outputDir)

with open(sys.argv[1], 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for row in reader:
        with open(outputDir + '/' + row[1] + '.fasta', 'w') as fastafile:
            fastafile.write('>' + row[1] + '\n' + row[0])
        with open ('sequenceFiles.csv', 'a') as seqfile:
            seqfile.write(row[1] + '.fasta,' + row[1] + '\n')
