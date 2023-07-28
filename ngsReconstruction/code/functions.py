import re
import os
import sys
import pandas as pd
from dnachisel.biotools import translate, reverse_complement
import configparser

# Method to read config file settings
# Helper file for reading the config file of interest for running the program
def read_config(configFile):
    config = configparser.ConfigParser()
    config.read(configFile)
    return config

# get the configuration file for the current
def getConfigFile(configDir):
    configFile = ''
    # Access the configuration file for this program (should only be one in the directory)
    programDir = os.path.realpath(configDir)
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

# make an output directory if it doesn't exist
def makeOutputDir(outputDir):
    # check if the path to the directory exists
    if not os.path.isdir(outputDir):
        print('Creating output directory: ' + outputDir + '.')
        # the below makes directories for the entire path
        os.makedirs(outputDir)
    else:
        print('Output Directory: ' + outputDir + ' exists.')

# FOR CREATING A CSV FILE OF SEQUENCE COUNTS PER BIN/M9/LB
#Checking the file exists or not
def check_file_empty(path_of_file):
    #Checking if file exist and it is empty
    return os.path.exists(path_of_file) 

# main functions     
# get counts for each of the files
def getCountsForFile(listSeq, dictSeq, colName, file):
    # convert to csv and keep the sequence, count, and percentage columns
    columns = ['Sequence', 'Count', 'Percentage']
    dfData = pd.read_csv(file, delimiter='\t', header=None, skiprows=4, usecols=[0,1,2])
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

# output sequence counts as a csv
def outputSequenceCountsCsv(listSeq, dir, outFile):
    dictSeq = {}
    # checking if file exist and it is empty
    fileExists = check_file_empty(outFile)
    if fileExists == False:
        for filename in sorted(os.listdir(dir)):
            # get one data file
            dataFile = os.path.join(dir, filename)
            # make sure it's a file
            if os.path.isfile(dataFile):
                # get the column name for this data from the file name (bin name, M9, LB, etc.)
                colName = getFilename(filename)
                dictSeq = getCountsForFile(listSeq, dictSeq, colName, dataFile)
        df = pd.DataFrame.from_dict(dictSeq)
        # transpose the dataframe so sequences are rows and bins and others are columns
        df_t = df.T
        df_t = df_t[sorted(df_t.columns)]
        df_t.to_csv(outFile)
    else:
        print("File exists. To rerun, delete " + outFile)

# get percents for each of the files
def getPercentsForFile(listSeq, dictSeq, colName, file):
    # convert to csv and keep the sequence, count, and percentage columns
    columns = ['Sequence', 'Count', 'Percentage']
    dfData = pd.read_csv(file, delimiter='\t', header=None, skiprows=4, usecols=[0,1,2])
    dfData.columns = columns
    # loop through all of the sequences and find count in dataframe
    for seq in listSeq:
        if seq not in dictSeq:
            dictSeq[seq] = {}
        # get data for the sequence in this file; if not found in file, set count as 0
        try:
            # search for the sequence as an index and get the count
            index = dfData.index[dfData['Sequence'] == seq].to_list()
            percent = dfData.loc[index[0], 'Percentage']
            dictSeq[seq][colName] = percent
        except:
            # if not found, set number for bin as 0
            dictSeq[seq][colName] = 0
    return dictSeq

# output percents as a csv
def outputSequencePercentsCsv(listSeq, dir, outFile):
    dictSeq = {}
    # checking if file exist and it is empty
    fileExists = check_file_empty(outFile)
    if fileExists == False:
        for filename in sorted(os.listdir(dir)):
            # get one data file
            dataFile = os.path.join(dir, filename)
            # make sure it's a file
            if os.path.isfile(dataFile):
                # get the column name for this data from the file name (bin name, M9, LB, etc.)
                colName = getFilename(filename)
                dictSeq = getPercentsForFile(listSeq, dictSeq, colName, dataFile)
        df = pd.DataFrame.from_dict(dictSeq)
        # transpose the dataframe so sequences are rows and bins and others are columns
        df_t = df.T
        df_t = df_t[sorted(df_t.columns)]
        df_t.to_csv(outFile)
    else:
        print("File exists. To rerun, delete " + outFile)

# gets a list of all of the unique sequences present in data within a directory
def getSequenceList(dir):
    allSeqs = []
    for file in os.listdir(dir):
        dataFile = os.path.join(dir, file)
        # get the sequence column (first column) and skip the summary data rows
        # TODO: fix this hardcoded 4
        seqColumn = pd.read_csv(dataFile, delimiter='\t', header=None, skiprows=4, usecols=[0])
        # convert that column to a list
        seqs = seqColumn.iloc[:,0].tolist()
        # add each value in the list to the allSeqs list
        for seq in seqs:
            allSeqs.append(seq) 
    # rid of the duplicate sequences in the list
    allSeqs = pd.unique(allSeqs).tolist()
    return allSeqs

# gets only sequences without unknown
def outputGoodSequenceDataframe(dir):
    listSeq = []
    listSegment = []
    for file in os.listdir(dir):
        dataFile = os.path.join(dir, file)
        # the below helps read csv files with differing numbers of columns: 
        # https://stackoverflow.com/questions/27020216/import-csv-with-different-number-of-columns-per-row-using-pandas
        # Delimiter
        delim = '\t'
        # The max column count a line in the file could have
        largest_column_count = 0
        # Loop the data lines
        with open(dataFile, 'r') as temp_f:
            # Read the lines
            lines = temp_f.readlines()
            for l in lines:
                # Count the column count for the current line
                column_count = len(l.split(delim)) + 1
                # Set the new most column count
                largest_column_count = column_count if largest_column_count < column_count else largest_column_count
        colName = ''
        # get the proper column names if a bin file or LB and M9
        if "C" in dataFile:
            colName = file[0:7] # name and rep for bins
        else:
            colName = file[0:11] # name, hour, and rep for LB/M9 
        # Generate column names (will be 0, 1, 2, ..., largest_column_count - 1)
        column_names = [i for i in range(0, largest_column_count)]
        dfData = pd.read_csv(dataFile, delimiter=delim, header=None, skiprows=4, names=column_names)
        dfData = dfData[dfData.iloc[:,3] != 'Unknown']
        numColumns = len(dfData.columns)
        dfData.insert(numColumns, "Replicate", colName)
        listSeq.extend(dfData.iloc[:,0].tolist())
        listSegment.extend(dfData.iloc[:,3].tolist())
    df = pd.DataFrame(zip(listSeq, listSegment), columns=['Sequence','Segment'])
    return df

# get the uniprot ids and add to a file
def appendColumnFromInputFile(df, colName, file):
    dfOut = pd.DataFrame()
    dfData = pd.read_csv(file, delimiter=',', index_col=0)
    if not colName in dfData.columns: 
        col = []
        # checking if file exist and it is empty
        for seq, row in dfData.iterrows():
            index = df.index[df['Sequence'] == seq].to_list()[0]
            value_from_col = df.loc[index, colName]
            col.append(value_from_col)
        dfOut = dfData
        dfOut.insert(0, colName, col)
        dfOut.to_csv(file)
    else:
        print("File with uniprot ids exists. To remake", file)

# converts ngs fastq files to more workable txt files
def convertFastqToTxt(fastqTotxt, namesFile, refFile, dataDir, outputDir):
    if len(os.listdir(outputDir)) == 0:
        # read in the file with names for output files
        df_names = pd.read_csv(namesFile, header=None)
        # convert it to a list
        list_names = df_names.iloc[:,0]
        # initialize lists for the datafiles for ngs sequences read in fwd and rvs
        fwdDatafiles = []
        rvsDatafiles = []
        # loop through the files in the data directory (holds the ngs files)
        sortedFiles = sorted(os.listdir(dataDir))
        for filename in sortedFiles:
            dataFile = os.path.join(dataDir, filename)
            # confirms that file is a fastq
            if os.path.isfile(dataFile) and 'fastq' in dataFile:
                dataFile = dataFile.replace(" ", "\ ") # replaces spaces so that directories with spaces can be located by linux command line
                # gets the direction 
                if dataFile.find("R1") != -1:
                    # add datafile to the fwd list
                    fwdDatafiles.append(dataFile)
                else:
                    # add datafile to the fwd list
                    rvsDatafiles.append(dataFile)
        # loop through the files and names and execute the fastq to txt file conversion for each file
        for dataFile, name in zip(fwdDatafiles, list_names):
            outputFile = outputDir+name+'.txt'
            execRunFastqTotxt = 'perl '+fastqTotxt+' --refFile '+refFile+' --seqFile '+dataFile+' --direction 1 > '+ outputFile 
            print(execRunFastqTotxt)
            os.system(execRunFastqTotxt)
            exit(0)
        print("Files successfully converted")
    else:
        print("Files already converted. If you would like to reconvert files, delete " + outputDir)

# insert column at the end of the dataframe
def insertAtEndOfDf(df, colName, col):
    numCol = len(df.columns)
    df.insert(numCol, colName, col)
    return df
