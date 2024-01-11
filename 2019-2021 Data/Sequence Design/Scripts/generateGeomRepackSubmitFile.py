#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 27 11:05:38 2021

@author: gloiseau
"""

import os
import pandas as pd
import numpy as np

#This program is meant to integrate seqDesign and geomRepack that finds all
#of the repack configuration files output from seqDesign and writing
#them into a submit file for geomRepacks to run

path = "/data02/gloiseau/Sequence_Design_Project/vdwSequenceDesign/sequenceDesign/"

#Find all of the config files from runs on
fileVec = np.array([])
submitLines = np.array([])
if (os.path.isdir(path)):
    for root, dirs, files in os.walk(path):
        #for d in dirs:
        #    designDir = d
        for name in files:
            #print os.path.join(root, name)
            if name.endswith((".config")):
                configFile = os.path.join(root, name)
                #configFile = configFile+name
                fileVec = np.append(fileVec, configFile)
                print (configFile)

for configFile in fileVec:
    line = "arguments = '--config $(pdbDir)"
    line = line+configFile+"'"
    submitLines = np.append(submitLines, line+configFile)
    #print(line)
