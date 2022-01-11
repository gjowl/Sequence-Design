#This script is meant to take the pdb clustered database and take the first pdb from each line

#TODO:
#figure out the best order to do my script:
#   1. read file by line
#   2. run executable file with portion from each line
#   3. write the list of pdbs I used to a test file
#   4. (optional) check against another list to extract only soluble or membrane proteins

########################################################################
#                             FUNCTIONS
########################################################################

def analyzeSolubleProteins():
    sp = input("Analyze soluble proteins?")
    if sp == "T" or sp == "t":
        return True
    else:
        return False

########################################################################
#                        READ ALL PDBS FROM PISCES
########################################################################
lines = []
strings = []
chains = []
extras = []

count = 0
#def code(*args):
    #with open('%s' %args, 'r') as inputfile:

cluster = input("Insert data cluster level in bc-## format: ")
sp = analyzeSolubleProteins()

if sp is True:
    protDir = "solubleProteins"
else:
    protDir = "membraneProteins"

#with open('/exports/home/gloiseau/Downloads/' + cluster + '.out', 'rt') as inputfile:
#    for line in inputfile:
#        lines.append(line)
#        if line[:4] not in strings: #this checks to see if it's nonredundant
#            strings.append(line[:4]) #I think this basically gets me all of the pdbids; could also get the chain of interest if I want?
#            chains.append(line[5:6])
with open('/exports/home/gloiseau/Downloads/' + cluster + '.out', 'rt') as inputfile:
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

#converted below to get the opposite strings to shorten membrane database
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

urls = []
filedirs = []
filenames = []
count = 0

#as of 2020_02_18: write a submit file instead of downloading the pdbs because just using OPM
executefile = open('/exports/home/gloiseau/submitMembrane' + cluster + '.txt', 'w')

args = 'arguments = "'
outputdir = ' --outputdir $(outputdir)/'
p = '"'
dirname = "/data02/gloiseau/Sequence_Design_Project/interhelicalCoordinates/" + protDir + "/opm_pdbs/pdbs/"
pdb = ".pdb"

for elem in stringsmem:
    executefile.write(args)
    executefile.write(dirname)
    executefile.write(elem)
    executefile.write(pdb)
    executefile.write(outputdir)
    executefile.write(elem) #gets me the pdb name from the file path
    executefile.write(p)
    executefile.write('\n')
    executefile.write('queue')
    executefile.write('\n')
executefile.close()

print("Finished!")
