"""
Created on Mon Sep 13 18:37:30 2021

@author: gjowl
"""
"""
This file is used to analyze the data from my sequence designs in an automated
way so that I don't have to manually do it every single time after the designs
are finished. It should take and read a file and set up all of the analysis for me.
"""
from datetime import date
from scipy import stats
from matplotlib import gridspec
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import re
import seaborn as sns

##############################################
#                 FUNCTIONS
##############################################

##############################################
#          Main Code
##############################################
dfPath = "C:\\Users\\gjowl\\Documents\\Senes Lab\\Design Research\\Sequence Design\\Analysis\\Design_files\\2021_10_16_rawDesignDataUnlinked.csv"
df = pd.read_csv(dfPath)

factorial = 1
for i in range(len(df['Sequence'])):
    seq = df['Sequence'][i]
    for j in seq:
        if j>4 and j<16:
            factorial = factorial*i


