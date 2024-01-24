# @Author: Gilbert Loiseau
# @Date:   2021-12-27
# @Filename: writeCATMConfig.py
# @Last modified by:   Gilbert Loiseau
# @Last modified time: 2022-03-01

from datetime import date
from scipy import stats
from matplotlib import gridspec
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import re
import seaborn as sns
import logomaker as lm
from utility import *
import logging

def writeConfigurationFile(df, fileName, batchName, baseDir, executable):
    queue = 'queue\n'
    with open(fileName, 'w') as submitFile:
        submitFile.write('batch_name = ' + batchName + '\n')
        submitFile.write('baseDir    = ' + baseDir + '\n\n')
        submitFile.write('executable = ' + executable+ '\n')
        submitFile.write('output     = $(baseDir)/out/$(Process).out\n')
        submitFile.write('log        = $(baseDir)/log/$(Process).log\n')
        submitFile.write('error      = $(baseDir)/err/$(Process).err\n\n')
        submitFile.write('stream_output = TRUE\n')
        submitFile.write('stream_error  = TRUE\n\n')
        submitFile.write('#Runs\n')
        for tm, id in zip(df['TM'],df['ID']):
            outputDir = "--pdbOutputDir " + baseDir + id
            sequence = "--fullSequence RAS"+tm+"LILIN"
            uniprotAccession = "--uniprotAccession "+id
            logFile = "--logFile " + baseDir + id + "/" + id + ".log"
            configLine = 'arguments = "--config $(configFile) ' + outputDir + " " + sequence + " " + uniprotAccession + " " + logFile + '"\n'
            submitFile.write(configLine)
            submitFile.write(queue)
        print("Config written: ", fileName)

#__main__
inputDir = "C:\\Users\\gjowl\\Documents\\"
outFile = inputDir+'CATMSubmitFile_2022_03_noIMM1_elec.condor'
batchName = 'CATM'
dirToSave = '/data02/gloiseau/CATM/2022_03_01_noIMM1_elec/'
executable = '/exports/home/mslib/trunk_AS/bin/CATM_v24.4'

inputFile = "C:\\Users\\gjowl\\Downloads\\Sequences for CATM 030122.xlsx"
df = pd.read_excel(inputFile)
writeConfigurationFile(df, outFile, batchName, dirToSave, executable)
