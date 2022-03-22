"""
Created on Mon Sep 13 18:37:30 2021

@author: gjowl
"""
"""
This file is used to analyze the data from my sequence designs in an automated
way so that I don't have to manually do it every single time after the designs
are finished. It should take and read a file and set up all of the analysis for me.
"""

from scipy import stats
from matplotlib import gridspec
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import re

##############################################
#               FILE INPUT
##############################################

name = "C:\\Users\\gjowl\\Documents\\Senes Lab\\Design_data\\Design_files\\allDesigns_2021_10_07.csv"
#name = "C:\\Users\\gjowl\\Documents\\Senes Lab\\Design_data\\Design_files\\designsSoFar.csv"

# Gets the header line to be used for the analysis
header = pd.read_csv(name, index_col=0, nrows=0).columns.tolist()

#TODO: something that may be nice would be to have a way to get the names of the header inputs and choosing what to use; in case I decide not to have some of these things in future implementations of the code
df = pd.read_csv(name, sep=",")

##############################################
#           MAKE SHEETS FOR OUTPUT
##############################################
dfall = df
df = df[df["VDWDiff"] < 0]
#dfBad = df[df["Total"] > 0]

dfT = df[df["Total"] < 0]
dfTH = dfT[dfT["HBONDDiff"] > -5]
df21 = df[df["Sequence"].str.len() == 21]
#df24 = df[df["Sequence"].str.len() == 24]

#dfT23 = df[df["Thread"] == 23]
#dfT24 = df[df["Thread"] == 24]
#dfT25 = df[df["Thread"] == 25]
#dfT26 = df[df["Thread"] == 26]
#dfT27 = df[df["Thread"] == 27]
#dfx1 = df[df["xShift"] == 8.04292]
#dfx2 = df[df["xShift"] == 8.27631]
#dfx3 = df[df["xShift"] == 8.84966]
#dfx4 = df[df["xShift"] == 10.007]
#dfr4 = df[df["Repack Level"] == 4]
#dfr5 = df[df["Repack Level"] == 5]
#Uncomment if want to get distribution between the angles
#dfLAll = dfall[dfall["crossingAngle"] > 10]
#dfRAll = dfall[dfall["crossingAngle"] < -10]

#dfL = dfTH[dfTH["crossingAngle"] > 10]
#dfR = dfTH[dfTH["crossingAngle"] < -10]

##############################################
#          GET AVERAGES FOR LEFT BINS
##############################################
dfA = pd.DataFrame()

vdw = np.array([])
hbond = np.array([])
imm1 = np.array([])
x = np.array([])
ca = np.array([])
ax = np.array([])
z = np.array([])
count = np.array([])

##############################################
#          GET AVERAGES FOR LEFT BINS
##############################################
numberBins = 6
i=0
while i < numberBins:
    if i == 0:
        tmp = df[df["Total"] < -30+(i*5)]
        vdw = np.append(vdw, tmp["VDWDiff"].mean())
        hbond = np.append(hbond, tmp["HBONDDiff"].mean())
        imm1 = np.append(imm1, tmp["IMM1Diff"].mean())
        x = np.append(x, tmp["xShift"].mean())
        #ca = np.append(ca, tmp["crossingAngle"].mean())
        #ax = np.append(ax, tmp["axialRotation"].mean())
        #z = np.append(z, tmp["zShift"].mean())
        count = np.append(count, tmp.shape[0])
    else:
        tmp = df[df["Total"] > -30+(i*5)]
        tmp = tmp[tmp["Total"] < -30+((i+1)*5)]
        vdw = np.append(vdw, tmp["VDWDiff"].mean())
        hbond = np.append(hbond, tmp["HBONDDiff"].mean())
        imm1 = np.append(imm1, tmp["IMM1Diff"].mean())
        x = np.append(x, tmp["xShift"].mean())
        #ca = np.append(ca, tmp["crossingAngle"].mean())
        #ax = np.append(ax, tmp["axialRotation"].mean())
        #z = np.append(z, tmp["zShift"].mean())
        count = np.append(count, tmp.shape[0])
    i+=1

dfA["VDWDifference"] = vdw
dfA["HbondDifference"] = hbond
dfA["IMM1Difference"] = imm1
dfA["xShift"] = x
#dfA["crossingAngle"] = ca
#dfA["axialRotation"] = ax
#dfA["zShift"] = z
dfA["Count"] = count

##############################################
#          GET AVERAGES FOR RIGHT BINS
##############################################
#TODO: use these values to make it make a certain number of bins for
#an amount of sequences (or for every 10 kcals or something)
#minL = dfL["Total"].min()
#print(minL)
#print(int( 5 * round( minL / 5. )))

dfA.index = ['x < -30','-30<x<-25','-25<x<-20','-20<x<-15','-15<x<-10','-10<x<-5']

##############################################
#               FILE OUTPUT
##############################################
#writer = pd.ExcelWriter('C:\\Users\\gjowl\\Documents\\'+date+'_test.xlsx',engine='xlsxwriter')
#workbook=writer.book
#worksheet=workbook.add_worksheet('Total Energy < -5')
#writer.sheets['Total Energy < -5'] = worksheet
with pd.ExcelWriter('C:\\Users\\gjowl\\Documents\\Senes Lab\\Design_data\\Analysis files\\2021_10_07_dataAnalysis.xlsx',engine='xlsxwriter') as writer:
    dfT.to_excel(writer,sheet_name='Total Energy < -5',startrow=0 , startcol=0)
    dfTH.to_excel(writer,sheet_name='HbondDifference > -5',startrow=0 , startcol=0)
    df21.to_excel(writer,sheet_name='21 Length',startrow=0 , startcol=0)
    #df24.to_excel(writer,sheet_name='24 Length',startrow=0 , startcol=0)
    dfA.to_excel(writer, sheet_name='Averages',startrow=0 , startcol=0)
    dfall.to_excel(writer,sheet_name='allData',startrow=0 , startcol=0)
    #dfT23.to_excel(writer,sheet_name='Thread 23',startrow=0 , startcol=0)
    #dfT24.to_excel(writer,sheet_name='Thread 24',startrow=0 , startcol=0)
    #dfT25.to_excel(writer,sheet_name='Thread 25',startrow=0 , startcol=0)
    #dfT26.to_excel(writer,sheet_name='Thread 26',startrow=0 , startcol=0)
    #dfT27.to_excel(writer,sheet_name='Thread 27',startrow=0 , startcol=0)
    #dfx1.to_excel(writer,sheet_name='xShift1',startrow=0 , startcol=0)
    #dfx2.to_excel(writer,sheet_name='xShift2',startrow=0 , startcol=0)
    #dfx3.to_excel(writer,sheet_name='xShift3',startrow=0 , startcol=0)
    #dfx4.to_excel(writer,sheet_name='xShift4',startrow=0 , startcol=0)
    #dfr4.to_excel(writer,sheet_name='Repack Level 4',startrow=0 , startcol=0)
    #dfr5.to_excel(writer,sheet_name='Repack Level 5',startrow=0 , startcol=0)
    #dfLAll.to_excel(writer,sheet_name='AllLeftHanded > 10',startrow=0 , startcol=0)
    #dfRAll.to_excel(writer,sheet_name='AllRightHanded < -10',startrow=0 , startcol=0)
