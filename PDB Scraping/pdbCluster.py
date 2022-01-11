#This script is meant to take the pdb clustered database and take the first pdb from each line

#TODO:
#figure out the best order to do my script:
#   1. read file by line
#   2. run executable file with portion from each line
#   3. write the list of pdbs I used to a test file
#   4. (optional) check against another list to extract only soluble or membrane proteins

########################################################################
#                        READ ALL PDBS FROM PISCES
########################################################################
lines = []
strings = []
extras = []
chains = []

count = 0
#def code(*args):
    #with open('%s' %args, 'r') as inputfile:

with open('/exports/home/gloiseau/Downloads/bc-30.out', 'rt') as inputfile:
    for line in inputfile:
        #if count < 5:
            #lines.append(line)
            l = line.split()
            pdb = l[0][:4]
            if pdb not in strings:
                if pdb not in extras:
                    strings.append(pdb)
            for i in range(1,len(l)):
                extras.append(l[i][:4])

membrane = []

print(strings[0])
print(strings[1])
print(strings[2])

########################################################################
#                       COMPARE TO OPM DATABASE
########################################################################

with open('/exports/home/gloiseau/pdbs_membrane.txt', 'rt') as protfile:
#with open('/exports/home/gloiseau/pdbs_bitopic.txt', 'rt') as protfile:
    for line in protfile:
        membrane.append(line[:4])

stringsnomem = []
stringsmem = []

for string in strings:
    if string.lower() not in membrane:
        stringsnomem.append(string.lower())
#I haven't check if I need to .lower() or the line[:4] yet, but it works as written above

for string in strings:
    if string.lower() in membrane:
        stringsmem.append(string.lower())

########################################################################
#                          WRITE PDB LISTS
########################################################################
outputall = open('/exports/home/gloiseau/allProt.txt', 'w')

for string in strings:
    outputall.write(string)
    outputall.write('\n')
outputall.close()

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
#                      DOWNLOAD PDB FILES
########################################################################
#creates a list of pdbs to be copy pasted into RCSBPDB to download zipped file

#uncomment numFiles if don't want to download all pdbs
#numFiles = 10

import requests

def is_downloadable(url):
    """
    Does the url contain a downloadable resource
    """
    h = requests.head(url, allow_redirects=True)
    header = h.headers
    content_type = header.get('content-type')
    if 'text' in content_type.lower():
        return False
    if 'html' in content_type.lower():
        return False
    return True

downloads = 'http://files.rcsb.org/download/'
#outpdbs = '/exports/home/gloiseau/solublepdbs/'
outpdbs = '/data02/gloiseau/Sequence_Design_Project/interhelicalCoordinates/solubleProteins/pdbs/'

urls = []
filedirs = []
filenames = []
count = 0
#Uncomment for membrane protein downloads
#for string in stringsmem:
#    urls.append(downloads + string + '.pdb')
#    filenames.append(outpdbs + string + '.pdb')

for string in stringsnomem:
    #if count < numFiles:
    urls.append(downloads + string + '.pdb')
        #filedirs.append(outpdbs + string + '/')
        #filenames.append(outpdbs + string + '/' + string + '.pdb')
    filenames.append(outpdbs + string + '.pdb')
    #count += 1

#this can check if urls are downloadable if not; Some files are cryoEM and have a different downloadable url that I haven't found out yet 

#TODO: comment out below if the pdbs are already downloaded; can probably add as an argument at some point
import urllib.request
import os

#if not os.path.exists(outpdbs):
#    os.makedirs(outpdbs)

brokenpdbs = open('/exports/home/gloiseau/brokenpdbs.txt', 'w')

filenum = 0
for url in urls:
    try:
        if is_downloadable(url) is True:
            #if not os.path.exists(filedirs[filenum]):
            #    os.makedirs(filedirs[filenum])
            #    urllib.request.urlretrieve(url, filenames[filenum])
            #else:
            #    urllib.request.urlretrieve(url, filenames[filenum])
            #if filenum >= 9500:
            urllib.request.urlretrieve(url, filenames[filenum])
    except:
        brokenpdbs.write(url)
        brokenpdbs.write('\n')
    filenum += 1
    print(filenum)
brokenpdbs.close()

########################################################################
#                      WRITE EXECUTABLE FILE
########################################################################

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

dirName = '/data02/gloiseau/Sequence_Design_Project/interhelicalCoordinates/membraneProteins/pdbs/opm_pdbs/pdbs/'

listOfFiles = getListOfFiles(dirName)

executefile = open('/exports/home/gloiseau/submit.txt', 'w')

args = 'arguments = "'
outputdir = ' --outputdir $(outputdir)/'
p = '"'

for elem in listOfFiles:
    executefile.write(args)
    executefile.write(elem)
    executefile.write(outputdir)
    executefile.write(os.path.basename(elem)[:4]) #gets me the pdb name from the file path
    executefile.write(p)
    executefile.write('\n')
    executefile.write('queue')
    executefile.write('\n')
executefile.close()

print("Finished!")
