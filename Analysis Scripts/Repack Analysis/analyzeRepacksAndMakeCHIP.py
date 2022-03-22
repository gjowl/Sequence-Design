# @Author: Gilbert Loiseau
# @Date:   2021-12-25
# @Filename: runDesignAndMakeCHIP.py
# @Last modified by:   Gilbert Loiseau
# @Last modified time: 2022/03/21

"""
This file will run multiple python scripts for analyzing repacked designs and prepare a CHIP to order
"""

import os
import helper

programPath = os.path.basename(__file__)
programName, programExt = os.path.splitext(programPath)

if __name__ == '__main__':
    #read in the config file
    config = helper.read_config()

    # make the output directory that these will all output to
    outputDir = config["main"]["outputDir"]
    analysisCodeDir = config["main"]["codeDir"]
    if not os.path.isdir(outputDir):
        print('Creating output directory: ' + outputDir + '.')
        os.mkdir(outputDir)
    else:
        print('Output Directory: ' + outputDir + ' exists.')
    # download the required packages for these programs, list of which is found in requirements.txt
    #exec(python -m pip install -r requirementsFile)

    # Compiles all backboneOptimized sequences and mutant data
    exec(open(analysisCodeDir+'/compileOptimizationDataFiles.py').read())
    # Analyzes the compiled backboneOptimization data
    exec(open(analysisCodeDir+'/optimizationAnalysis.py').read())#This is the version of optimizedBackboneAnalysis for data on the server
    # Take the backbone analysis and convert the sequences to a CHIP
    exec(open(analysisCodeDir+'/prepareCHIP.py').read())
