# @Author: Gilbert Loiseau
# @Date:   2021-12-25
# @Filename: runDesignAndMakeCHIP.py
# @Last modified by:   Gilbert Loiseau
# @Last modified time: 2022/03/17

"""
This file will run multiple python scripts for compiling and then analyzing design data.
"""

import os
import helper
# TODO: would be great to also have a way to automatically download packages that aren't downloaded to run the code

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
    # Haven't tried this yet
    #exec(python -m pip freeze > requirementsFile)
    #exec(python -m pip install -r requirementsFile)

    #TODO: remember, I ran the design on an external server. Can I make a way to do that here? likely not?
    # Compiles design energy files from all design directories
    exec(open(analysisCodeDir+'/compileAllDesignEnergyFiles.py').read())
    print("Design energy files compiled")
    #TODO: add in a wait time
    # Analyzes designs and outputs a submit file filled with sequences for backboneOptimization
    #exec(open(analysisCodeDir+'/analyzeDesignData.py').read())#version of designAnalyzer.py for my data on the server
    print("Designs analyzed")#TODO: output the number of "successful designs"?
    #TODO: do I also add in a way to run the next step here? I'll need to assume that these files are all found in the same directory
    #exec("condor_submit backboneOptimization.condor")
    # Compiles all backboneOptimized sequences and mutant data
    #exec(open(analysisCodeDir+'/compileOptimizationDataFiles.py').read())
    ## Analyzes the compiled backboneOptimization data
    #exec(open(analysisCodeDir+'/optimizationAnalysis.py').read())#This is the version of optimizedBackboneAnalysis for data on the server
    ## Take the backbone analysis and convert the sequences to a CHIP
    #exec(open(analysisCodeDir+'/prepareCHIP.py').read())
