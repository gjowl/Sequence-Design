import re
import os
import sys
import pandas as pd

def getConfigFile(file):
    configFile = ''
    # Access the configuration file for this program (should only be one in the directory)
    programPath = os.path.realpath(file)
    programDir, programFile = os.path.split(programPath)
    programName, programExt = os.path.splitext(programFile)
    fileList = os.listdir(programDir)
    for file in fileList:
        fileName, fileExt = os.path.splitext(file)
        if fileExt == '.config':
            configFile = programDir + '/' + file
    if configFile == '':
        sys.exit("No config file present in script directory!")
    return configFile

# get filename separate from type and directory
def getFilename(file):
    programPath = os.path.realpath(file)
    programDir, programFile = os.path.split(programPath)
    filename, programExt = os.path.splitext(programFile)
    return filename

def makeOutputDir(outputDir):
    # check if the path to the directory exists
    if not os.path.isdir(outputDir):
        print('Creating output directory: ' + outputDir + '.')
        # the below makes directories for the entire path
        os.makedirs(outputDir)
    else:
        print('Output Directory: ' + outputDir + ' exists.')

# load a file with reference sequences and other information
def readReferenceFile(refFile):
    #get file object
    f = open(refFile, "r")
    #read all lines
    lines = f.readlines()
    #setup output dictionary
    dictSequence = {}
    #traverse through lines one by one
    for line in lines:
        lineSplit = re.split(r'\t', line.strip())
        seqInfo = ''
        i = 0 
        while i < 6:
            seqInfo += lineSplit[i]+"\t"
            i += 1
        seqName = lineSplit[6]
        dictSequence[seqName] = seqInfo 
    #close file
    f.close
    return dictSequence

# converts ngs fastq files to more workable txt files
def convertFastqToTxt(fastqTotxt, config, dataDir, outputDir):
    if len(os.listdir(outputDir)) == 0:
        for filename in os.listdir(dataDir):
            dataFile = os.path.join(dataDir, filename)
            # check to see if the file exists and if it is a fastq file
            if os.path.isfile(dataFile) and dataFile.find("fastq") != -1:
                print(dataFile)
                dataFile = dataFile.replace(" ", "\ ") # replaces spaces so that directories with spaces can be located by linux command line
                # gets the direction 
                if dataFile.find("R1") != -1:
                    execRunFastqTotxt = 'python3 '+fastqTotxt+' '+config+' '+dataFile+' '+'F'
                    print(execRunFastqTotxt)
                    os.system(execRunFastqTotxt)
                else:#TODO: get this working for reverse
                    continue
                    execRunFastqTotxt = 'python3 '+fastqTotxt+' '+config+' '+dataFile+' '+'R'
                    print(execRunFastqTotxt)
                    os.system(execRunFastqTotxt)
        print("Files successfully converted")
    else:
        print("Files already converted. If you would like to reconvert files, delete " + outputDir)

# FOR CREATING A CSV FILE OF SEQUENCE COUNTS PER BIN/M9/LB
#Checking the file exists or not
def check_file_empty(path_of_file):
    #Checking if file exist and it is empty
    return os.path.exists(path_of_file) 

def outputSequenceCountsCsv(listSeq, dir, outFile):
    dictSeq = {}
    # checking if file exist and it is empty
    fileExists = check_file_empty(outFile)
    print(fileExists)
    if fileExists == False:
        for filename in os.listdir(dir):
            # get one data file
            dataFile = os.path.join(dir, filename)
            # make sure it's a file
            if os.path.isfile(dataFile):
                # get the column name for this data from the file name (bin name, M9, LB, etc.)
                colName = filename[6:13]
                dictSeq = getCountsForFile(listSeq, dictSeq, colName, dataFile)
                #for key, value in dictSeq.items():
                #    for k, v in value.items():
                #        if v > 0:
                #            print(key, k, v)
        df = pd.DataFrame.from_dict(dictSeq)
        # transpose the dataframe so sequences are rows and bins and others are columns
        df_t = df.T
        df_t = df_t[sorted(df_t.columns)]
        df_t.to_csv(outFile)
    else:
        print("File exists. To rerun, delete " + outFile)
        
def getCountsForFile(listSeq, dictSeq, colName, file):
    # convert to csv and keep the sequence, count, and percentage columns
    columns = ['Sequence', 'Count', 'Percentage']
    dfData = pd.read_csv(file, delimiter='\t', header=None, skiprows=3, usecols=[0,1,2])
    dfData.columns = columns
    # loop through all of the sequences and find count in dataframe
    for seq in listSeq:
        if seq not in dictSeq:
            dictSeq[seq] = {}
        # get data for the sequence in this file; if not found in file, set count as 0
        try:
            # search for the sequence as an index and get the count
            index = dfData.index[dfData['Sequence'] == seq].to_list()
            count = dfData.loc[index[0], 'Count']
            dictSeq[seq][colName] = count
        except:
            # if not found, set number for bin as 0
            dictSeq[seq][colName] = 0
    return dictSeq

