'''
    - Run as: python3 keepNonRedundantPdbs.py -pdbDir /path/to/pdb/files -proteinList /path/to/proteinList
'''

import os, sys, argparse, pandas as pd

# initialize the parser
parser = argparse.ArgumentParser(description='gets nonredundant pdbs and writes an executable file for the cluster')
# add the necessary arguments
parser.add_argument('-pdbDir','--directory', type=str, help='the directory with pdbs to search through')
parser.add_argument('-proteinList','--proteinList', type=str, help='the list of nonredundant pdbs from the pdb database')
# extract the arguments into variables
args = parser.parse_args()
pdbDir = args.directory
proteinList = args.proteinList

# functions
# get list of files in a directory
def getListOfFiles(dirName):
    # create a list of file and sub directories 
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

if __name__ == '__main__':

    # initialize variables for compiling the list of pdb data (sequence similarity bc from pdb: https://www.rcsb.org/docs/programmatic-access/file-download-services)
    strings = [] # nonredundant pdbs
    redundant = [] # redundant pdbs
    # get the current directory
    currDir = os.getcwd()

    # get the list of pdbs that should be accepted
    with open(proteinList, 'rt') as outputfile:
        # loop through the file
        for line in outputfile:
            l = line.split()
            pdb = l[0][:4].lower()
            # check if the pdb is already in the list of pdbs
            if pdb not in strings:
                # check if the pdb is in the list of redundant
                if pdb not in redundant:
                    strings.append(pdb)
                else:
                    # loop through the rest of the pdbs on that line until you find one that is not in the list of strings and redundant
                    for i in range(1, len(l)):
                        pdb2 = l[i][:4].lower()
                        if pdb2 not in strings and pdb2 not in redundant:
                            strings.append(pdb)
                            break
                        else:
                            continue
            # add the rest of the pdbs on the line to the list of redundant pdbs
            for i in range(1,len(l)):
                redundant.append(l[i][:4].lower())
        # close the file
        outputfile.close()

    # the below code didn't work, so I decided to just copy the files to a new directory and then extract the list of files from that directory
    # save the list of pdbs to a file 
    #with open(currDir + '/nonRedundantPdbs.txt', 'w') as outputfile:
    #    for elem in strings:
    #        outputfile.write(elem)
    #        outputfile.write('\n')
    #    outputfile.close() 

    # get the list of files in the pdb directory
    allPdbFiles = getListOfFiles(pdbDir)

    # define the output directory
    outputDir = currDir + '/nonRedundantPdbs'
    os.makedirs(outputDir, exist_ok=True)
    nonredundantPdbs = []
    # get the filename from the path
    for i in range(len(allPdbFiles)):
        filename = os.path.basename(allPdbFiles[i])
        pdb = filename[:4].lower()
        print(i)
        if pdb in strings:
            # copy the file to the new directory
            print("Copying file: ", i, filename)
            os.system('cp ' + allPdbFiles[i] + ' ' + outputDir)
            nonredundantPdbs.append(filename)
        else:
            continue

    # get the list of nonredundant pdbs from the directory
    nonRedundantPdbs = getListOfFiles(currDir + '/nonRedundantPdbs')
    # write executable csv
    dirName = '/'
    submitFileName = 'submit.csv'
    submitfile = open(currDir + '/' + submitFileName, 'w')
    args = 'arguments = "'
    outputdir = ' --outputdir $(outputdir)/'
    p = '"'
    for i in range(len(nonRedundantPdbs)):
        elem = os.path.basename(nonRedundantPdbs[i])
        submitfile.write(os.path.basename(elem))
        submitfile.write(',')
        submitfile.write(os.path.basename(elem)[:4])
        submitfile.write('\n')
    print("Finished!")