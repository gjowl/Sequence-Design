# -*- coding: utf-8 -*-
"""
Created on Tue May  4 15:41:03 2021

@author: gjowl

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

date = input("Insert date of design data to analyze in year_month_day (2021_05_04) format: ")

name = "C:\\Users\\gjowl\\Documents\\"+date+"_designData.csv"

header = ['1','2','Total','Dimer','Monomer','VDWDimer','VDWMonomer','VDWDifference'
          ,'HbondDimer','HbondMonomer','HbondDifference','IMM1Monomer',
          'IMM1Dimer','IMM1Difference','MonomerNoIMM1','Baseline','Baseline-Monomer'
          ,'HbondMonomerNoIMM1','VDWMonomerNoIMM1','MonomerSelfBaseline',
          'DimerSelfBaseline','SelfDifference','MonomerPairBaseline','DimerPairBaseline'
          ,'PairDifference','EnergyBeforeLocalMC','startXShift','startCrossingAngle'
          ,'startAxialRotation','startZShift','xShift','crossingAngle'
          ,'axialRotation','zShift','Sequence','PDBPath','Thread','InterfacePositions']

df = pd.read_csv(name, sep=",", names=header, dtype={'InterfacePositions': object})
#df['InterfacePositions'] = df['InterfacePositions'].astype(str)

##############################################
#  RID OF SEQUENCES WITH TOO MANY METHIONINES
##############################################
#dfNoM = df[df["Sequence"].str.count('M', re.I)
dflessPolar = df[df["Sequence"].str.count('M', re.I)
           +df["Sequence"].str.count('S', re.I)
           +df["Sequence"].str.count('C', re.I)
           +df["Sequence"].str.count('T', re.I) < 5]

##############################################
#           MAKE SHEETS FOR OUTPUT
##############################################
dfT = dflessPolar[dflessPolar["Total"] < 0]
dfTH = dfT[dfT["HbondDifference"] > -5]
dfL = dfTH[dfTH["crossingAngle"] > 10]
dfR = dfTH[dfTH["crossingAngle"] < -10]

##############################################
#          GET AVERAGES FOR LEFT BINS
##############################################
dfA = pd.DataFrame()

vdw = np.array([])
vdwsd = np.array([])
imm1 = np.array([])
imm1sd = np.array([])
hbond = np.array([])
hbondsd = np.array([])
baseline = np.array([])
x = np.array([])
xsd = np.array([])
ca = np.array([])
casd = np.array([])
ax = np.array([])
z = np.array([])
count = np.array([])

##############################################
#          GET AVERAGES FOR LEFT BINS
##############################################
#Bin 1
dfLA1 = dfL[dfL["Total"] < -30]
vdw = np.append(vdw, dfLA1["VDWDifference"].mean())
vdwsd = np.append(vdwsd, dfLA1["VDWDifference"].std())
imm1 = np.append(imm1, dfLA1["IMM1Difference"].mean())
imm1sd = np.append(imm1sd, dfLA1["IMM1Difference"].std())
hbond = np.append(hbond, dfLA1["HbondDifference"].mean())
hbondsd = np.append(hbondsd, dfLA1["HbondDifference"].std())
baseline = np.append(baseline, dfLA1["Baseline-Monomer"].mean())
x = np.append(x, dfLA1["xShift"].mean())
xsd = np.append(xsd, dfLA1["xShift"].std())
ca = np.append(ca, dfLA1["crossingAngle"].mean())
casd = np.append(casd, dfLA1["crossingAngle"].std())
ax = np.append(ax, dfLA1["axialRotation"].mean())
z = np.append(z, dfLA1["zShift"].mean())
count = np.append(count, dfLA1.shape[0])

#Bin 2
dfLA2 = dfL[dfL["Total"] < -25]
dfLA2 = dfLA2[dfLA2["Total"] > -30]
vdw = np.append(vdw, dfLA2["VDWDifference"].mean())
vdwsd = np.append(vdwsd, dfLA2["VDWDifference"].std())
imm1 = np.append(imm1, dfLA2["IMM1Difference"].mean())
imm1sd = np.append(imm1sd, dfLA2["IMM1Difference"].std())
hbond = np.append(hbond, dfLA2["HbondDifference"].mean())
hbondsd = np.append(hbondsd, dfLA2["HbondDifference"].std())
baseline = np.append(baseline, dfLA2["Baseline-Monomer"].mean())
x = np.append(x, dfLA2["xShift"].mean())
xsd = np.append(xsd, dfLA2["xShift"].std())
ca = np.append(ca, dfLA2["crossingAngle"].mean())
casd = np.append(casd, dfLA2["crossingAngle"].std())
ax = np.append(ax, dfLA2["axialRotation"].mean())
z = np.append(z, dfLA2["zShift"].mean())
count = np.append(count, dfLA2.shape[0])

#Bin 3
dfLA3 = dfL[dfL["Total"] < -20]
dfLA3 = dfLA3[dfLA3["Total"] > -25]
vdw = np.append(vdw, dfLA3["VDWDifference"].mean())
vdwsd = np.append(vdwsd, dfLA3["VDWDifference"].std())
imm1 = np.append(imm1, dfLA3["IMM1Difference"].mean())
imm1sd = np.append(imm1sd, dfLA3["IMM1Difference"].std())
hbond = np.append(hbond, dfLA3["HbondDifference"].mean())
hbondsd = np.append(hbondsd, dfLA3["HbondDifference"].std())
baseline = np.append(baseline, dfLA3["Baseline-Monomer"].mean())
x = np.append(x, dfLA3["xShift"].mean())
xsd = np.append(xsd, dfLA3["xShift"].std())
ca = np.append(ca, dfLA3["crossingAngle"].mean())
casd = np.append(casd, dfLA3["crossingAngle"].std())
ax = np.append(ax, dfLA3["axialRotation"].mean())
z = np.append(z, dfLA3["zShift"].mean())
count = np.append(count, dfLA3.shape[0])

#Bin 4
dfLA4 = dfL[dfL["Total"] < -15]
dfLA4 = dfLA4[dfLA4["Total"] > -20]
vdw = np.append(vdw, dfLA4["VDWDifference"].mean())
vdwsd = np.append(vdwsd, dfLA4["VDWDifference"].std())
imm1 = np.append(imm1, dfLA4["IMM1Difference"].mean())
imm1sd = np.append(imm1sd, dfLA4["IMM1Difference"].std())
hbond = np.append(hbond, dfLA4["HbondDifference"].mean())
hbondsd = np.append(hbondsd, dfLA4["HbondDifference"].std())
baseline = np.append(baseline, dfLA4["Baseline-Monomer"].mean())
x = np.append(x, dfLA4["xShift"].mean())
xsd = np.append(xsd, dfLA4["xShift"].std())
ca = np.append(ca, dfLA4["crossingAngle"].mean())
casd = np.append(casd, dfLA4["crossingAngle"].std())
ax = np.append(ax, dfLA4["axialRotation"].mean())
z = np.append(z, dfLA4["zShift"].mean())
count = np.append(count, dfLA4.shape[0])

#Bin 5
dfLA5 = dfL[dfL["Total"] < -10]
dfLA5 = dfLA5[dfLA5["Total"] > -15]
vdw = np.append(vdw, dfLA5["VDWDifference"].mean())
vdwsd = np.append(vdwsd, dfLA5["VDWDifference"].std())
imm1 = np.append(imm1, dfLA5["IMM1Difference"].mean())
imm1sd = np.append(imm1sd, dfLA5["IMM1Difference"].std())
hbond = np.append(hbond, dfLA5["HbondDifference"].mean())
hbondsd = np.append(hbondsd, dfLA5["HbondDifference"].std())
baseline = np.append(baseline, dfLA5["Baseline-Monomer"].mean())
x = np.append(x, dfLA5["xShift"].mean())
xsd = np.append(xsd, dfLA5["xShift"].std())
ca = np.append(ca, dfLA5["crossingAngle"].mean())
casd = np.append(casd, dfLA5["crossingAngle"].std())
ax = np.append(ax, dfLA5["axialRotation"].mean())
z = np.append(z, dfLA5["zShift"].mean())
count = np.append(count, dfLA5.shape[0])

#Bin 6
dfLA6 = dfL[dfL["Total"] < -5]
dfLA6 = dfLA6[dfLA6["Total"] > -10]
vdw = np.append(vdw, dfLA6["VDWDifference"].mean())
vdwsd = np.append(vdwsd, dfLA6["VDWDifference"].std())
imm1 = np.append(imm1, dfLA6["IMM1Difference"].mean())
imm1sd = np.append(imm1sd, dfLA6["IMM1Difference"].std())
hbond = np.append(hbond, dfLA6["HbondDifference"].mean())
hbondsd = np.append(hbondsd, dfLA6["HbondDifference"].std())
baseline = np.append(baseline, dfLA6["Baseline-Monomer"].mean())
x = np.append(x, dfLA6["xShift"].mean())
xsd = np.append(xsd, dfLA6["xShift"].std())
ca = np.append(ca, dfLA6["crossingAngle"].mean())
casd = np.append(casd, dfLA6["crossingAngle"].std())
ax = np.append(ax, dfLA6["axialRotation"].mean())
z = np.append(z, dfLA6["zShift"].mean())
count = np.append(count, dfLA6.shape[0])

vdwL = vdw
imm1L = imm1
hbondL = hbond
baselineL = baseline
xL = x
caL = ca
axL = ax
zL = z
countL = count

dfA["VDWDifferenceLeft"] = vdwL
dfA["vdwsd"] = vdwsd
dfA["HbondDifferenceLeft"] = hbondL
dfA["hbondsd"] = hbondsd
dfA["IMM1DifferenceLeft"] = imm1L
dfA["IMM1sd"] = imm1sd
dfA["BaselineDifferenceLeft"] = baselineL
dfA["xShiftLeft"] = xL
dfA["xShiftsd"] = xsd
dfA["crossingAngleLeft"] = caL
dfA["crossingAnglesd"] = casd
dfA["axialRotationLeft"] = axL
dfA["zShiftLeft"] = zL
dfA["CountLeft"] = countL

vdw = np.array([])
imm1 = np.array([])
hbond = np.array([])
baseline = np.array([])
vdwsd = np.array([])
imm1sd = np.array([])
hbondsd = np.array([])
x = np.array([])
xsd = np.array([])
ca = np.array([])
casd = np.array([])
ax = np.array([])
z = np.array([])
count = np.array([])

##############################################
#          GET AVERAGES FOR RIGHT BINS
##############################################
#TODO: use these values to make it make a certain number of bins for
#an amount of sequences (or for every 10 kcals or something)
#minL = dfL["Total"].min()
#print(minL)
#print(int( 5 * round( minL / 5. )))

#Bin 1
dfRA1 = dfR[dfR["Total"] < -30]
vdw = np.append(vdw, dfRA1["VDWDifference"].mean())
vdwsd = np.append(vdwsd, dfRA1["VDWDifference"].std())
imm1 = np.append(imm1, dfRA1["IMM1Difference"].mean())
imm1sd = np.append(imm1sd, dfRA1["IMM1Difference"].std())
hbond = np.append(hbond, dfRA1["HbondDifference"].mean())
hbondsd = np.append(hbondsd, dfRA1["HbondDifference"].std())
baseline = np.append(baseline, dfRA1["Baseline-Monomer"].mean())
x = np.append(x, dfRA1["xShift"].mean())
xsd = np.append(xsd, dfRA1["xShift"].std())
ca = np.append(ca, dfRA1["crossingAngle"].mean())
casd = np.append(casd, dfRA1["crossingAngle"].std())
ax = np.append(ax, dfRA1["axialRotation"].mean())
z = np.append(z, dfRA1["zShift"].mean())
count = np.append(count, dfRA1.shape[0])

#Bin 2
dfRA2 = dfR[dfR["Total"] < -25]
dfRA2 = dfRA2[dfRA2["Total"] > -30]
vdw = np.append(vdw, dfRA2["VDWDifference"].mean())
vdwsd = np.append(vdwsd, dfRA2["VDWDifference"].std())
imm1 = np.append(imm1, dfRA2["IMM1Difference"].mean())
imm1sd = np.append(imm1sd, dfRA2["IMM1Difference"].std())
hbond = np.append(hbond, dfRA2["HbondDifference"].mean())
hbondsd = np.append(hbondsd, dfRA2["HbondDifference"].std())
baseline = np.append(baseline, dfRA2["Baseline-Monomer"].mean())
x = np.append(x, dfRA2["xShift"].mean())
xsd = np.append(xsd, dfRA2["xShift"].std())
ca = np.append(ca, dfRA2["crossingAngle"].mean())
casd = np.append(casd, dfRA2["crossingAngle"].std())
ax = np.append(ax, dfRA2["axialRotation"].mean())
z = np.append(z, dfRA2["zShift"].mean())
count = np.append(count, dfRA2.shape[0])

#Bin 3
dfRA3 = dfR[dfR["Total"] < -20]
dfRA3 = dfRA3[dfRA3["Total"] > -25]
vdw = np.append(vdw, dfRA3["VDWDifference"].mean())
vdwsd = np.append(vdwsd, dfRA3["VDWDifference"].std())
imm1 = np.append(imm1, dfRA3["IMM1Difference"].mean())
imm1sd = np.append(imm1sd, dfRA3["IMM1Difference"].std())
hbond = np.append(hbond, dfRA3["HbondDifference"].mean())
hbondsd = np.append(hbondsd, dfRA3["HbondDifference"].std())
baseline = np.append(baseline, dfRA3["Baseline-Monomer"].mean())
x = np.append(x, dfRA3["xShift"].mean())
xsd = np.append(xsd, dfRA3["xShift"].std())
ca = np.append(ca, dfRA3["crossingAngle"].mean())
casd = np.append(casd, dfRA3["crossingAngle"].std())
ax = np.append(ax, dfRA3["axialRotation"].mean())
z = np.append(z, dfRA3["zShift"].mean())
count = np.append(count, dfRA3.shape[0])

#Bin 4
dfRA4 = dfR[dfR["Total"] < -15]
dfRA4 = dfRA4[dfRA4["Total"] > -20]
vdw = np.append(vdw, dfRA4["VDWDifference"].mean())
vdwsd = np.append(vdwsd, dfRA4["VDWDifference"].std())
imm1 = np.append(imm1, dfRA4["IMM1Difference"].mean())
imm1sd = np.append(imm1sd, dfRA4["IMM1Difference"].std())
hbond = np.append(hbond, dfRA4["HbondDifference"].mean())
hbondsd = np.append(hbondsd, dfRA4["HbondDifference"].std())
baseline = np.append(baseline, dfRA4["Baseline-Monomer"].mean())
x = np.append(x, dfRA4["xShift"].mean())
xsd = np.append(xsd, dfRA4["xShift"].std())
ca = np.append(ca, dfRA4["crossingAngle"].mean())
casd = np.append(casd, dfRA4["crossingAngle"].std())
ax = np.append(ax, dfRA4["axialRotation"].mean())
z = np.append(z, dfRA4["zShift"].mean())
count = np.append(count, dfRA4.shape[0])

#Bin 5
dfRA5 = dfR[dfR["Total"] < -10]
dfRA5 = dfRA5[dfRA5["Total"] > -15]
vdw = np.append(vdw, dfRA5["VDWDifference"].mean())
vdwsd = np.append(vdwsd, dfRA5["VDWDifference"].std())
imm1 = np.append(imm1, dfRA5["IMM1Difference"].mean())
imm1sd = np.append(imm1sd, dfRA5["IMM1Difference"].std())
hbond = np.append(hbond, dfRA5["HbondDifference"].mean())
hbondsd = np.append(hbondsd, dfRA5["HbondDifference"].std())
baseline = np.append(baseline, dfRA5["Baseline-Monomer"].mean())
x = np.append(x, dfRA5["xShift"].mean())
xsd = np.append(xsd, dfRA5["xShift"].std())
ca = np.append(ca, dfRA5["crossingAngle"].mean())
casd = np.append(casd, dfRA5["crossingAngle"].std())
ax = np.append(ax, dfRA5["axialRotation"].mean())
z = np.append(z, dfRA5["zShift"].mean())
count = np.append(count, dfRA5.shape[0])

#Bin 6
dfRA6 = dfR[dfR["Total"] < -5]
dfRA6 = dfRA6[dfRA6["Total"] > -10]
vdw = np.append(vdw, dfRA6["VDWDifference"].mean())
vdwsd = np.append(vdwsd, dfRA6["VDWDifference"].std())
imm1 = np.append(imm1, dfRA6["IMM1Difference"].mean())
imm1sd = np.append(imm1sd, dfRA6["IMM1Difference"].std())
hbond = np.append(hbond, dfRA6["HbondDifference"].mean())
hbondsd = np.append(hbondsd, dfRA6["HbondDifference"].std())
baseline = np.append(baseline, dfRA6["Baseline-Monomer"].mean())
x = np.append(x, dfRA6["xShift"].mean())
xsd = np.append(xsd, dfRA6["xShift"].std())
ca = np.append(ca, dfRA6["crossingAngle"].mean())
casd = np.append(casd, dfRA6["crossingAngle"].std())
ax = np.append(ax, dfRA6["axialRotation"].mean())
z = np.append(z, dfRA6["zShift"].mean())
count = np.append(count, dfRA6.shape[0])

vdwR = vdw
imm1R = imm1
hbondR = hbond
baselineR = baseline
xR = x
caR = ca
axR = ax
zR = z
countR = count

dfA["VDWDifferenceRight"] = vdwR
dfA["VDWsd"] = vdwsd
dfA["HbondDifferenceRight"] = hbondR
dfA["Hbondsd"] = hbondsd
dfA["IMM1DifferenceRight"] = imm1R
dfA["IMM1sd"] = imm1sd
dfA["BaselineDifferenceRight"] = baselineR
dfA["xShiftRight"] = xR
dfA["xShiftsd"] = xsd
dfA["crossingAngleRight"] = caR
dfA["crossingAnglesd"] = casd
dfA["axialRotationRight"] = axR
dfA["zShiftRight"] = zR
dfA["CountRight"] = countR

dfA.index = ['x < -30','-30<x<-25','-25<x<-20','-20<x<-15','-15<x<-10','-10<x<-5']

##############################################
#               FILE OUTPUT
##############################################
#writer = pd.ExcelWriter('C:\\Users\\gjowl\\Documents\\'+date+'_test.xlsx',engine='xlsxwriter')   
#workbook=writer.book
#worksheet=workbook.add_worksheet('Total Energy < -5')
#writer.sheets['Total Energy < -5'] = worksheet
with pd.ExcelWriter('C:\\Users\\gjowl\\Documents\\'+date+'_analyzedDesignData.xlsx',engine='xlsxwriter') as writer:
    df.to_excel(writer,sheet_name='allData',startrow=0 , startcol=0)
    dflessPolar.to_excel(writer,sheet_name='PolarAAs < 5',startrow=0 , startcol=0)
    dfT.to_excel(writer,sheet_name='Total Energy < -5',startrow=0 , startcol=0)
    dfTH.to_excel(writer,sheet_name='HbondDifference > -5',startrow=0 , startcol=0)
    dfL.to_excel(writer,sheet_name='LeftHanded > 10',startrow=0 , startcol=0)
    dfR.to_excel(writer,sheet_name='RightHanded < -10',startrow=0 , startcol=0)
    dfA.to_excel(writer, sheet_name='Averages',startrow=0 , startcol=0)
    #dfNoM.to_excel(writer, sheet_name='LessM',startrow=0 , startcol=0)