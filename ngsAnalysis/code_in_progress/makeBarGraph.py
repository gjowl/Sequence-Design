import plotly.express as px
import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# read in data file from command line file options
inputFile = sys.argv[1]

# read in data file as dataframe
df = pd.read_csv(inputFile)

# set up output directory
programPath = os.path.realpath(inputFile)
programDir, programFile = os.path.split(programPath)
outputDir = programDir +'/'

# data columns to plot
list_columns = ['VDWDimer-VDWMonomerDiff','HBONDDimer-HBONDMonomerDiff','IMM1Dimer-IMM1MonomerDiff'] 
#fig = px.bar(df, x='Sequence', y='EnergyScore',
#             hover_data=list_columns, color=list_color,
#             labels={'pop':'population of Canada'}, height=400)
#fig.show()
n = len(df)
x = np.arange(n)
width = 1
# get the VDW energy difference column
VDWDimerMonomerDiff = df['VDWDimer-VDWMonomerDiff']
# get the HBOND energy difference column
HBONDDimerMonomerDiff = df['HBONDDimer-HBONDMonomerDiff']
# multiply the HBOND energy difference column by -1 to make it positive
HBONDDimerMonomerDiff = HBONDDimerMonomerDiff*-1
# get the IMM1 energy difference column
IMM1DimerMonomerDiff = df['IMM1Dimer-IMM1MonomerDiff']
# multiply the IMM1 energy difference column by -1 to make it positive
IMM1DimerMonomerDiff = IMM1DimerMonomerDiff*-1
# setup the bar plots for each energy difference
fig, ax = plt.subplots()
p1 = plt.bar(x, VDWDimerMonomerDiff, width, color='b')
p2 = plt.bar(x, HBONDDimerMonomerDiff, width, color='r', bottom=VDWDimerMonomerDiff)
#p3 = plt.bar(x, IMM1DimerMonomerDiff, width, color='g', bottom=HBONDDimerMonomerDiff)
# change the dpi to make the image smaller
fig.set_dpi(20000)
plt.ylabel('Energy')
plt.title('Energy Plot')
plt.xticks(x, df['Sequence'])
plt.yticks(np.arange(-70, 0, 10))
plt.legend((p2[0], p1[0]), ('HBOND', 'VDW'))
plt.show()
# save plot
fig.savefig(outputDir+'energyPlot.png')

