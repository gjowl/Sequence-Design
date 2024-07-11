import os, sys, configparser, argparse
import pandas as pd

description = '''
This contains outputs for the pdbOptimizationAnalysis code. It extracts the energetics from a C++ program that predicts
structures of mutant proteins based on a given dimeric pdb structure. The analysis for those energies, according to the 
below given options, is found within this directory. Directories named as follows:
    - clash: trim by the clashing mutant data
    - mutant_cutoff: fluorescence cutoff that the mutant must be less than to accept
    - percent_cutoff: another cutoff for mutants where the mutant fluorescence must be at least this much less than the WT to be accepted
    - number_of_mutants: the number of mutants necessary to be accepted for the WT design to be accepted
'''

'''
    parse the command line arguments
'''
# initialize the parser
parser = argparse.ArgumentParser(description='Adjust the reconstructed fluorescence by the flow fluorescence of the controls')

# add the necessary arguments
parser.add_argument('-config','--config', type=str, help='the input configuration file')
parser.add_argument('-outputDir','--outputDir', type=str, help='the output directory')
parser.add_argument('-helperScript','--helperScript', type=str, help='the helper script file')

# extract the arguments into variables
args = parser.parse_args()
configFile = args.config
helperScript = args.helperScript
# import the functions from the helper code and get the program name
exec(open(helperScript).read())
programName = getFilename(__file__) # toxgreenConversion

# default value for the output directory (if not given, the current working directory is used + the program name)
outputDir = f'{os.getcwd()}/{programName}'
if args.outputDir is not None:
    outputDir = args.outputDir
    os.makedirs(outputDir, exist_ok=True)

'''
    read in the config file options and set up the directory to be able to rerun the program
'''
# get the config file options
globalConfig = read_config(configFile)
config = globalConfig[programName]

# Config file options
inputDir   = config["inputDir"]
rawDataDir = config['rawDataDir']

'''
    copy the input files into the output directory
'''
# copy the original config file to the output directory
os.system(f'cp {configFile} {outputDir}/originalConfig.config')

# copy the input files directory to the output directory
inputDir, config = copyInputFiles(inputDir, outputDir, config) # inputDir is now the new input directory within the output directory, and config has been updated with the new file paths

'''
    reading the config file options
'''
# input files
kdeFile              = f'{inputDir}/{config["kdeFile"]}'
requirementsFile     = f'{inputDir}/{config["requirementsFile"]}'
toxgreenFile         = f'{inputDir}/{config["toxgreenFile"]}'
maltoseFile          = f'{inputDir}/{config["maltoseFile"]}'
sequenceFile         = f'{inputDir}/{config["sequenceFile"]}'
mutantFile           = f'{inputDir}/{config["mutantFile"]}'

# get the script directory
scriptDir = config['scriptDir']

# other inputs
maltoseCol           = config["maltoseCol"] # the column name for the maltose data to use

# separate the cutoffs by commas
mutant_cutoffs = [float(x) for x in config['mutant_cutoff'].split(',')]
percent_cutoffs = [float(x) for x in config['percent_cutoff'].split(',')]
number_of_mutants_cutoffs = [int(x) for x in config['number_of_mutants_cutoff'].split(',')]

# check if there is a sequence for the maltose test
maltoseSeq = None
if 'maltoseSeq' in config:
    maltoseSeq = f'{config["maltoseSeq"]}'

# copy the config file to the output directory (setting up the rerun.config file for the next run)
# if this works well, you should just be able to run: python3 PATHTOCODE/PROGRAMNAME rerun.config
config['inputDir'] = inputDir
# write the config options to rerun configuration file
with open(f'{outputDir}/rerun.config', 'w') as f:
    # write the program name
    f.write(f'[{programName}]\n')
    for option in config:
        f.write(f'{option} = {config[option]}\n')
    # close the file
    f.close()

if __name__ == "__main__":
    # write README file 
    writeReadMe(globalConfig, outputDir)
    print(f'Running {programName}...')
    # install the requirements
    #execInstallRequirements = "pip install -r " + requirementsFile + " | { grep -v 'already satisfied' || :; }" 
    #os.system(execInstallRequirements)

    # strip the sequence ends (the first and last 3 amino acids) from the sequence file since some of the sequences have alanine vs leucine ends (overwrites the strippedSequenceFile if it already exists)
    strippedSequenceFile = f'strippedSequenceFile'
    execStripSequenceEnds = f'python3 {scriptDir}/stripSequenceEnds.py -inFile {toxgreenFile} -outFile {strippedSequenceFile} -outDir {outputDir}'
    print(f' - Running: {execStripSequenceEnds}')
    #os.system(execStripSequenceEnds)

    # keep only the maltose passing data
    strippedMaltosePassingFile = f'{strippedSequenceFile}_maltose'
    execKeepMaltoseData = f'python3 {scriptDir}/keepMaltoseData.py -inFile {outputDir}/{strippedSequenceFile}.csv -maltoseFile {maltoseFile} -maltoseCol {maltoseCol} -maltoseSeq {maltoseSeq} -outFile {strippedMaltosePassingFile} -outDir {outputDir}'
    print(f' - Running: {execKeepMaltoseData}')
    #os.system(execKeepMaltoseData)

    # compile the energy files (overwrites the dataFile if it already exists)
    dataFile = f'energyData' # defined here so that it can be used in further programs
    execCompileEnergyFiles = f'python3 {scriptDir}/compileFilesFromDirectories.py -inDir {rawDataDir} -outFile {dataFile} -outDir {outputDir}'
    print(f' - Running: {execCompileEnergyFiles}')
    #os.system(execCompileEnergyFiles) 

    # get the dataFile name without the extension
    dataFilename = os.path.splitext(dataFile)[0]
    percentGpaFile = f'{dataFilename}_percentGpa'
    # add the percent gpa to the dataframe
    execAddPercentGpA = f'python3 {scriptDir}/addPercentGpaToDf.py -inFile {outputDir}/{dataFilename}.csv -toxgreenFile {outputDir}/{strippedSequenceFile}.csv -outFile {percentGpaFile} -outDir {outputDir}' 
    print(f' - Running: {execAddPercentGpA}')
    #os.system(execAddPercentGpA)

    ## keep only the data passing the maltose test for both the sequence and mutant files
    maltosePassingFile = f'{percentGpaFile}_maltose'
    execKeepMaltoseData = f'python3 {scriptDir}/keepMaltoseData.py -inFile {outputDir}/{percentGpaFile}.csv -maltoseFile {maltoseFile} -maltoseCol {maltoseCol} -maltoseSeq {maltoseSeq} -outFile {maltosePassingFile} -outDir {outputDir}'
    print(f' - Running: {execKeepMaltoseData}')
    #os.system(execKeepMaltoseData)
    # keep the maltose data for the sequence and mutant files 
    sequence_maltosePassingFile = f'sequenceFile_maltosePassing'
    mutant_maltosePassingFile = f'mutantFile_maltosePassing'
    execKeepMaltoseDataSeqFile = f'python3 {scriptDir}/keepMaltoseData.py -inFile {sequenceFile} -maltoseFile {maltoseFile} -maltoseCol {maltoseCol} -maltoseSeq {maltoseSeq} -outFile {sequence_maltosePassingFile} -outDir {outputDir}'
    print(f' - Running: {execKeepMaltoseDataSeqFile}')
    #os.system(execKeepMaltoseDataSeqFile)
    execKeepMaltoseDataMutFile = f'python3 {scriptDir}/keepMaltoseData.py -inFile {mutantFile} -maltoseFile {maltoseFile} -maltoseCol {maltoseCol} -maltoseSeq {maltoseSeq} -outFile {mutant_maltosePassingFile} -outDir {outputDir} -sequenceColumn Mutant'
    print(f' - Running: {execKeepMaltoseDataMutFile}')
    #os.system(execKeepMaltoseDataMutFile)
    
    # check if you want to analyze clash data
    for number_of_mutants_cutoff in number_of_mutants_cutoffs:
        for mutant_cutoff in mutant_cutoffs:
            for percent_cutoff in percent_cutoffs:
                # convert the cutoffs to integers
                mut, perc, num = int(mutant_cutoff*100), int(percent_cutoff*100), int(number_of_mutants_cutoff)
                clashOutputDir = f'{outputDir}/clash_{mut}_{perc}_{num}'
                execclashCheck = f'python3 {scriptDir}/keepBestClashing_v2.py -seqFile {outputDir}/{sequence_maltosePassingFile}.csv -mutFile {outputDir}/{mutant_maltosePassingFile}.csv -outDir {clashOutputDir} -mutCutoff {mutant_cutoff} -percentWtCutoff {percent_cutoff} -numMutants {number_of_mutants_cutoff}'
                #execclashCheck = f'python3 {scriptDir}/keepBestClashing.py -seqFile {sequenceFile} -mutFile {mutantFile} -outDir {clashOutputDir} -mutCutoff {mutant_cutoff} -percentWtCutoff {percent_cutoff} -numMutants {number_of_mutants_cutoff}'
                print(f' - Running: {execclashCheck}')
                os.system(execclashCheck)
                # loop through the files in the clashOutputDir
                for filename in os.listdir(clashOutputDir):
                    # check if the file is a csv
                    print(filename)
                    if not filename.endswith('.csv'):
                        continue
                    # define variables for the analysis
                    file_outputDir = f'{clashOutputDir}/{os.path.splitext(filename)[0]}'
                    file_to_analyze = 'lowestEnergySequences' # made in analyzeData.py (which is used by the combineFilesAndPlot.py script which plots scatters; this file gets used for the kde plots)
                    # check if the directory exists and continue if it does
                    #if os.path.isdir(file_outputDir):
                    #    continue
                    # check if the directory is the mutant directory
                    execAnalyzeclash = f'python3 {scriptDir}/combineFilesAndPlot.py -seqFile {clashOutputDir}/{filename} -energyFile {outputDir}/{maltosePassingFile}.csv -outDir {file_outputDir} -percentCutoff {percent_cutoff} -codeDir {scriptDir}'
                    print(f' - Running: {execAnalyzeclash}')
                    os.system(execAnalyzeclash)
                    #if 'wt' in filename:
                    #    execAnalyzeclash = f'python3 {scriptDir}/combineFilesAndPlot.py -seqFile {clashOutputDir}/{filename} -energyFile {outputDir}/{maltosePassingFile}.csv -outDir {file_outputDir} -percentCutoff {percent_cutoff} -codeDir {scriptDir}'
                    #    print(f' - Running: {execAnalyzeclash}')
                    #    os.system(execAnalyzeclash)
                    #else:
                    #    execAnalyzeclash = f'python3 {scriptDir}/combineFilesAndPlot.py -seqFile {clashOutputDir}/{filename} -energyFile {outputDir}/{strippedMaltosePassingFile}.csv -outDir {file_outputDir} -percentCutoff {percent_cutoff} -codeDir {scriptDir}'
                    #    print(f' - Running: {execAnalyzeclash}')
                    #    os.system(execAnalyzeclash)
                    # plot kde plots of geometries from a sequence file made by combineFilesAndPlot.py
                    execPlotKde = f'python3 {scriptDir}/makeKdePlots.py -kdeFile {kdeFile} -dataFile {file_outputDir}/{file_to_analyze}.csv -outDir {file_outputDir}'
                    print(f' - Running: {execPlotKde}')
                    os.system(execPlotKde)
                # convert to delta G
                deltaG_outFile = f'{file_to_analyze}_deltaG.csv'
                execConvertToDeltaG = f'python3 {scriptDir}/convertToDeltaG.py -inFile {file_outputDir}/{file_to_analyze}.csv -outDir {file_outputDir} -outFile {deltaG_outFile}'
                print(f' - Running: {execConvertToDeltaG}')
                os.system(execConvertToDeltaG)

                # graph the delta G
                execGraphDeltaG = f'python3 {scriptDir}/graphDeltaG.py -inFile {file_outputDir}/{deltaG_outFile}.csv -outDir {file_outputDir}'
                print(f' - Running: {execGraphDeltaG}')
                os.system(execGraphDeltaG)

    # analyze the data
    #execAnalyzeData = f'python3 {codeDir}/analyzeData.py -inFile {outputDir}/{outputFile}.csv -outDir {outputDir}' 
    execAnalyzeData = f'python3 {scriptDir}/analyzeData.py -inFile {outputDir}/{maltosePassingFile}.csv -outDir {outputDir}' 
    print(f' - Running: {execAnalyzeData}')
    os.system(execAnalyzeData)