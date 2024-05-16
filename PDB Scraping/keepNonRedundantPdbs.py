import os, sys, argparse, pandas as pd

# initialize the parser
parser = argparse.ArgumentParser(description='gets nonredundant pdbs and writes an executable file for the cluster')
# add the necessary arguments
parser.add_argument('-pdbDir','--directory', type=str, help='the directory with pdbs to search through')
parser.add_argument('-proteinList','--proteinList', type=str, help='the list of nonredundant pdbs from the pdb database')
# extract the arguments into variables
args = parser.parse_args()
dirName = args.directory
proteinList = args.proteinList

# functions
# get list of files in a directory
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

if __name__ == '__main__':

    # initialize variables for compiling the list of pdb data (sequence similarity bc from pdb: https://www.rcsb.org/docs/programmatic-access/file-download-services)
    lines = []
    strings = []
    extras = []
    chains = []

    # get the current directory
    currDir = os.getcwd()

    # get the list of pdbs that should be accepted
    with open(proteinList, 'rt') as outputfile:
        for line in outputfile:
            l = line.split()
            pdb = l[0][:4].lower()
            if pdb not in strings:
                if pdb not in extras:
                    strings.append(pdb)
                else:
                    for i in range(1, len(l)):
                        pdb2 = l[i][:4].lower()
                        if pdb2 not in strings and pdb2 not in extras:
                            strings.append(pdb)
                            break
                        else:
                            continue
            for i in range(1,len(l)):
                extras.append(l[i][:4].lower())
        # close the file
        outputfile.close()
    
    # get the list of files in the directory
    allPdbFiles = getListOfFiles(dirName)

    # define the output directory
    outputDir = currDir + '/nonRedundantPdbs'
    # make directory if it doesn't exist
    os.makedirs(outputDir, exist_ok=True)
    # 
    nonredundantPdbs = []
    # get the filename from the path
    for i in range(len(allPdbFiles)):
        filename = os.path.basename(allPdbFiles[i])
        pdb = filename[:4].lower()
        if pdb in strings:
            # copy the file to the new directory
            #print("Copying file: ", filename)
            os.system('cp ' + allPdbFiles[i] + ' ' + outputDir)
            nonredundantPdbs.append(filename)
        else:
            continue
    
    # write executable file
    dirName = '/'
    submitFileName = 'submit.txt'
    submitfile = open(currDir + '/' + submitFileName, 'w')
    args = 'arguments = "'
    outputdir = ' --outputdir $(outputdir)/'
    p = '"'
    for elem in nonredundantPdbs:
        submitfile.write(os.path.basename(elem))
        submitfile.write(',')
        submitfile.write(os.path.basename(elem)[:4])
        submitfile.write('\n')
    submitfile.close()
    print("Finished!")
