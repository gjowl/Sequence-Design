'''
File: d:\github\Sequence-Design\ngsReconstruction\CHIP2_analysisCode\clashCheckMain.py
Project: d:\github\Sequence-Design\ngsReconstruction\CHIP2_analysisCode
Created Date: Monday August 28th 2023
Author: gjowl
-----
Last Modified: Monday August 28th 2023 7:44:33 pm
Modified By: gjowl
-----
Description:
This is the main code for extracting clashing data from sort-seq data. It uses the computationally predicted vdW to check if the expected
clash led to a decrease in fluorescence. It then plots the computationally predicted fluorescence vs the experimentally measured fluorescence.
These output files can also be used in other plotting code, specifically the code in ngsReconstruction\2023-8-28_calcEnergyCompare\code\analyzeData.py,
which utilizes the energetic data from my backbone optimization code on all of my sequences (see ngsReconstruction\2023-8-28_calcEnergyCompare\code\README.md)
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------
'''
import os, sys, pandas as pd

# read in the command line arguments
configFile = sys.argv[1]
cwd = os.getcwd()

# read in the input file as a dataframe
df = pd.read_csv(configFile)
#codeDir = f'/mnt/d/github/Sequence-Design/ngsReconstruction/CHIP2_analysisCode'
codeDir = f'/home/loiseau@ad.wisc.edu/github/Sequence-Design/ngsReconstruction/CHIP2_analysisCode'

# loop through all rows in the dataframe
for index, row in df.iterrows():
    inputDir = row['Input Directory']
    sequenceFile = f'{inputDir}/{row["Sequence File"]}'
    mutantFile = f'{inputDir}/{row["Mutant File"]}'
    wt_cutoff = row['WT Fluor Cutoff']
    mutant_cutoff = row['Mutant Fluor Cutoff']
    percent_cutoff = row['Percent WT Cutoff']
    #outputDir = f'{cwd}/clash_atLeastOneMutant/wt_{wt_cutoff}_mutant_{mutant_cutoff}_percent_{percent_cutoff}'
    #outputDir = f'{cwd}/clash_atLeastOneMutant/wt_{wt_cutoff}_mutant_{mutant_cutoff}'
    outputDir = f'{cwd}/clash_GASright/wt_{wt_cutoff}_mutant_{mutant_cutoff}'

    execClashCheck = f'python3 {codeDir}/checkMostClashyMutants.py {sequenceFile} {mutantFile} {outputDir} {wt_cutoff} {mutant_cutoff} {percent_cutoff}'
    os.system(execClashCheck)

    execGraphComputationVsExperiment = f'python3 {codeDir}/graphComputationVsExperiment.py {outputDir}/wtGreaterThanMutant.csv {outputDir}'
    os.system(execGraphComputationVsExperiment)