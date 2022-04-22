# -*- coding: utf-8 -*-
# @Author: Gilbert Loiseau
# @Date:   2021-12-25
# @Last Modified by:   Gilbert Loiseau
# @Last Modified time: 2022-04-22 15:39:51
"""
This file will be used to generate a condor submit file for running programs in batches using condor.
"""

# Use the utilityFunctions function to get the name of this program
programName = getProgramName(sys.argv[0])
configFile = sys.argv[1]

# Read in configuration file:
globalConfig = helper.read_config(configFile)
config = globalConfig[programName]

# Config file options:
batchName        = config["batchName"]
executable       = config["executable"]
condorOutputDir  = config["output"]
condorLogDir     = config["log"]
condorErrDir     = config["error"]
fileName         = config["fileName"]
header           = config["header"]
arguments        = config["arguments"]
variables        = config["variables"]
variableFile     = config["variableFile"]

with open(fileName, "w+") as o:
    o.write("Submit file for ", header, "\n")
    o.write("batch_name    = ", batchName, "n")
    o.write("baseDir       = ", outputDir, "\n")
    o.write("\n#Executable\n")
    o.write("executable    = ", executable, "\n")
    o.write("output        = ", condorOutputDir, "\n")
    o.write("log           = ", condorLogDir, "\n")
    o.write("error         = ", condorErrDir, "\n")
    o.write("stream_output = TRUE", "\n")
    o.write("stream_error  = TRUE", "\n")
    o.write("Arguments = ", arguments)
    o.write("queue ", variables, " from ", variableFile)
