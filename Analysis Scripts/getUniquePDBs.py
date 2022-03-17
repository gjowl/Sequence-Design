# @Author: Gilbert Loiseau
# @Date:   2021-12-09
# @Filename: getUniquePDBs.py
# @Last modified by:   Gilbert Loiseau
# @Last modified time: 2021-12-09



#This file will take a csv of pdbs and read every other row of them,
#then get the sequence entropy

from datetime import date
from scipy import stats
from matplotlib import gridspec
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import re
import seaborn as sns
from designFunctions import *

today = date.today()
today = today.strftime("%Y_%m_%d")
inputFile = "C:\\Users\\gjowl\\Downloads\\membranePDBs.csv"
df = pd.read_csv(inputFile, sep=',')

df = df.drop_duplicates(subset=['PDB'], keep="first")

outputDir = "C:\\Users\\gjowl\\Documents\\"
outFile = outputDir + '2021_12_06_UniquePDBs.xlsx'
writer = pd.ExcelWriter(outFile)
writeDataframeToSpreadsheet(df, writer, "No Duplicates")
writer.save()
writer.close()
