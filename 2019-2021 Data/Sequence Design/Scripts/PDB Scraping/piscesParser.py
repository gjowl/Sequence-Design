#This script is meant to take the PISCES database and take the first pdb from each line and choose one pair of interacting chains to analyze
#I can use the chains as inputs into Alessandro's code somehow?

#TODO:
#figure out the best order to do my script:
#   1. read file by line
#   2. run executable file with portion from each line
#   3. write the list of pdbs I used to a test file
#   4. (optional) check against another list to extract only soluble or membrane proteins

########################################################################
#                          HOUSEKEEPING VARIABLES
########################################################################

import re

lines = []
strings = []
chains = []
pattern = re.compile(">")

count = 0
#def code(*args):
    #with open('%s' %args, 'r') as inputfile:

########################################################################
#                        READ ALL PDBS FROM PISCES
########################################################################
with open('/exports/home/gloiseau/Downloads/pdbaa.nr', 'rt') as inputfile:
    for line in inputfile:
        if pattern.search(line) != None:
            lines.append(line)
            #if count == 0:
            #    strings.append(line[1:5]) #I think this basically gets me all of the pdbids; could also get the chain of interest if I want?
            #    chains.append(line[6:6])
            #    count == -1
            if line[1:5] not in strings: #this checks to see if it's nonredundant; PISCES is ordered well so I could make this faster by just checking the previous line
                strings.append(line[1:5]) #I think this basically gets me all of the pdbids; could also get the chain of interest if I want?
                chains.append(line[6:6])

membrane = []

########################################################################
#                       COMPARE TO OPM DATABASE
########################################################################

#with open('/exports/home/gloiseau/pdbs_membrane.txt', 'rt') as protfile:
with open('/exports/home/gloiseau/pdbs_bitopic.txt', 'rt') as protfile:
    for line in protfile:
        membrane.append(line[:4])

print(membrane[0])

stringsnomem = []
stringsmem = []

for string in strings:
    if string.lower() not in membrane:
        stringsnomem.append(string.lower())
#I haven't check if I need to .lower() or the line[:4] yet, but it works as written above

#converted below to get the opposite strings to shorten membrane database
for string in strings:
    if string.lower() in membrane:
        stringsmem.append(string.lower())
#outputfile = open('/exports/home/gloiseau/testfile.txt', 'w')
#
#outputfile.write('PDBIDs')
#outputfile.write('\n')
#
#for string in strings:
#    outputfile.write(string)
#    outputfile.write('\n')
#outputfile.close()

########################################################################
#                          WRITE PDB LIST
########################################################################
outputnomem = open('/exports/home/gloiseau/nomembraneProt.txt', 'w')

for string in stringsnomem:
    outputnomem.write(string)
    outputnomem.write('\n')
outputnomem.close()

outputmem = open('/exports/home/gloiseau/membraneProt.txt', 'w')

for string in stringsmem:
    outputmem.write(string)
    outputmem.write('\n')
outputmem.close()
########################################################################
#                      WRITE EXECUTABLE FILE
########################################################################
#the below creates the run portions of a condor file; I haven't yet decided if I should just call it a condor file and then change all of the other parts
#executefile = open('/exports/home/gloiseau/submit.txt', 'w')
executefile = open('/exports/home/gloiseau/submit.txt', 'w')

#args = 'arguments = "/exports/home/gloiseau/Downloads/pdbs_bitopic/'
args = 'arguments = "/exports/home/gloiseau/solublepdbs/'
outputdir = '.pdb --outputdir $(outputdir)/'
p = '"'
#for string in stringsnomem:
#    executefile.write(args)
#    executefile.write(string)
#    executefile.write(outputdir)
#    executefile.write(string)
#    executefile.write('\n')
#    executefile.write('queue')
#    executefile.write('\n')
#executefile.close()
#above works to get all soluble proteins (but also includes non-helical)

#19-12-20: going to run the interhelicalCoordinates on just bitopic membrane proteins for small sample

count = 0
#changing the number of count changes the amount of jobs to run
for string in stringsnomem:
    if count < 1000:
        executefile.write(args)
        executefile.write(string)
        executefile.write(outputdir)
        executefile.write(string)
        executefile.write(p)
        executefile.write('\n')
        executefile.write('queue')
        executefile.write('\n')
    count += 1
executefile.close()

#the below can download the multiple pdb file of interest from the internet and save them
import urllib.request

downloads = 'http://files.rcsb.org/download/'
outpdbs = '/exports/home/gloiseau/solublepdbs/'

urls = []
filenames = []
count = 0

for string in stringsnomem:
    if count < 1000:
        urls.append(downloads + string + '.pdb')
        filenames.append(outpdbs + string + '.pdb')
    count += 1
#for string in stringsnomem:
#    if count < 1000:
#url = "http://files.rcsb.org/download/200l.pdb"
#filename = "/exports/home/gloiseau/solublepdbs/200l.pdb"

filenum = 0
for url in urls:
    urllib.request.urlretrieve(url, filenames[filenum])
    filenum += 1
#urllib.request.urlretrieve("http://files.rcsb.org/download/200l.pdb", "/exports/home/gloiseau/solublepdbs/200l.pdb")
#urllib.urlretrieve("http://files.rcsb.org/download/" + downloadpdb, "/exports/home/gloiseau/solublepdbs/" + downloadpdb)
#urllib.request.urlretrieve(downloadpdb, outs)

#can now replace open file with any file in shell set to an arg1, arg2, etc.
   
#######################################################################
#                   Parsing lines with Python 3.0
#######################################################################i

#make sure you read the most correct version next time :P

#splits the data by line

#reverts the data from a list to a workable script
