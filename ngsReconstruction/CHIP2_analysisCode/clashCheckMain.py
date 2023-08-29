import os, sys, pandas as pd

# read in the command line arguments
configFile = sys.argv[1]
cwd = os.getcwd()

# read in the input file as a dataframe
df = pd.read_csv(configFile)

# loop through all rows in the dataframe
for index, row in df.iterrows():
    inputDir = row['Input Directory']
    sequenceFile = f'{inputDir}/{row["Sequence File"]}'
    mutantFile = f'{inputDir}/{row["Mutant File"]}'
    wt_cutoff = row['WT Fluor Cutoff']
    mutant_cutoff = row['Mutant Fluor Cutoff']
    percent_cutoff = row['Percent WT Cutoff']
    outputDir = f'{cwd}/clash/wt_{wt_cutoff}_mutant_{mutant_cutoff}_percent_{percent_cutoff}'

    execClashCheck = f'python3 CHIP2_analysisCode/checkMostClashyMutants.py {sequenceFile} {mutantFile} {outputDir} {wt_cutoff} {mutant_cutoff} {percent_cutoff}'
    os.system(execClashCheck)

    execGraphComputationVsExperiment = f'python3 CHIP2_analysisCode/graphComputationVsExperiment.py {outputDir}/wtGreaterThanMutant.csv {outputDir}'
    os.system(execGraphComputationVsExperiment)