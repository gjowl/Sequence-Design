# @Author: Gilbert Loiseau
# @Date:   2021-12-25
# @Filename: runDesignAndMakeCHIP.py
# @Last modified by:   Gilbert Loiseau
# @Last modified time: 2022/03/21

"""
This file will run multiple python scripts for compiling and then analyzing design data.
"""

import sys
import os
import helper
import configparser

#Get program name to access corresponding configuration file
#configFile = '/exports/home/gloiseau/github/Sequence-Design/Design Analysis/' + programName + '.config'
programPath = os.path.realpath(__file__)
programDir, programFile = os.path.split(programPath)
programName, programExt = os.path.splitext(programFile)
fileList = os.listdir(programDir)

#class noConfigException():
#    def __init__(self):
#        self.message = "No config file found! Make sure there is a <fileName>.config file found in the program directory"
#    def print_error(self):
#        print(self.message)

configFile = ''
#try:
#    configFile = getConfigFile()
#except noConfigException as error:
#    print("Bad input : {configFile}")
#    print("{error.message}")

def getConfigFile():
    configFile = ''
    for file in fileList:
        fileName, fileExt = os.path.splitext(file)
        if fileExt == '.config':
            print(fileExt)
            configFile = programDir + '\\' + file
    if configFile == '':
        print("No config given! Break")
    return configFile

configFile = getConfigFile()
print('Config1:',configFile)

if __name__ == '__main__':
    #read in the config file
    config = helper.read_config(configFile)

    # make the output directory that these will all output to
    outputDir = config["main"]["outputDir"]
    print("DIR: "+outputDir)
    analysisCodeDir = config["main"]["codeDir"]

    compileCode = analysisCodeDir+'/compileAllDesignEnergyFiles.py'
    os.system(compileCode)
    if not os.path.isdir(outputDir):
        print('Creating output directory: ' + outputDir + '.')
        os.mkdir(outputDir)
    else:
        print('Output Directory: ' + outputDir + ' exists.')
    # download the required packages for these programs, list of which is found in requirements.txt
    # Haven't tried this yet
    #tips for requirements files https://pip.pypa.io/en/latest/reference/requirements-file-format/#requirements-file-format
    #exec(python -m pip install -r 'requirements.txt')
    #exec(python -m pip freeze > requirementsFile)
    #exec(python -m pip install -r 'requirements.txt')

    #TODO: remember, I ran the design on an external server. Can I make a way to do that here? likely not?
    # Compiles design energy files from all design directories
    compileCode = analysisCodeDir+'/compileAllDesignEnergyFiles.py'
    os.system(compileCode)
    exec(open(analysisCodeDir+'/compileAllDesignEnergyFiles.py').read())
    print("Design energy files compiled")
    # Analyzes designs and outputs a submit file filled with sequences for backboneOptimization
    exec(open(analysisCodeDir+'/analyzeDesignData.py').read())#version of designAnalyzer.py for my data on the server
    print("Designs analyzed")#TODO: output the number of "successful designs"?
    #TODO: do I also add in a way to run the next step here? I'll need to assume that these files are all found in the same directory
    #exec("condor_submit backboneOptimization.condor")
