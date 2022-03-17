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
def plotKdeOverlay(dfKde, xData, yData, xAxis, yAxis, type):
    #Variable set up depending on data that I'm running
    if xAxis == "xShift":
        xmin = 6
        xmax = 12
        ymin = -100
        ymax = 100
        X, Y = np.mgrid[xmin:xmax:24j, ymin:ymax:40j]
    elif xAxis == "Z1":
        xmin = 0
        xmax = 6
        ymin = 0
        ymax = 6
        X, Y = np.mgrid[xmin:xmax:24j, ymin:ymax:24j]
    elif xAxis == "Rot1":
        xmin = 0
        xmax = 100
        ymin = 0
        ymax = 100
        X, Y = np.mgrid[xmin:xmax:40j, ymin:ymax:40j]
    x = dfKde.loc[:, xAxis]
    y = dfKde.loc[:, yAxis]

    if type == 1:
        name = "Negative"
    if type == 2:
        name = "PositiveVDW"
    if type == 3:
        name = "Clashing"
    if type == 4:
        name = "all"
    if type == 5:
        name = "DimerNoIMM1"
    if type == 6:
        name = "21Neg"
    if type == 7:
        name = "24Neg"
    #Kernel Density Estimate Calculation
    positions = np.vstack([X.ravel(), Y.ravel()])
    values = np.vstack([x, y])
    kernel = stats.gaussian_kde(values)
    kernel.set_bandwidth(bw_method='silverman')
    Z = np.reshape(kernel(positions).T, X.shape)

    # Plotting code below
    fig, ax = plt.subplots()
    plt.grid(True)
    plt.xlabel(xAxis)
    plt.ylabel(yAxis)
    plt.title(xAxis+"_v_"+yAxis+"_"+name)
    ax.use_sticky_edges = False
    q = ax.imshow(np.rot90(Z), cmap=plt.cm.Blues,
        extent=[xmin, xmax, ymin, ymax], aspect="auto")
    ax.plot(xData, yData, 'k.', markersize=3, color = "Red")
    x = dfKde.loc[:, xAxis]
    y = dfKde.loc[:, yAxis]
    #ax.plot(x, y, 'k.', markersize=2)
    #ax.margins(x=2, y=2)
    ax.set_xlim([xmin, xmax])
    ax.set_ylim([ymin, ymax])
    #ax.set_aspect(0.5)
    if xAxis == "xShift":
           ax.set_xticks([6,7,8,9,10,11,12])
    elif xAxis == "Rot1":
           ax.set_xticks([0,20,40,60,80,100])
    elif xAxis == "Z1":
           ax.set_xticks([0,1,2,3,4,5,6])
    axes = plt.gca()

    #save and show plot figure
    today = date.today()
    today = today.strftime("%Y_%m_%d")
    plt.colorbar(q)
    plt.savefig(today+"_"+xAxis+"_v_"+yAxis+"_"+name+".png", bbox_inches='tight')
    plt.show()

    figSNS, axSNS = plt.subplots()
    plt.title(xAxis+"_v_"+yAxis+"_"+name)
    if xAxis == "Distance":
        sns.kdeplot(dfKde[xAxis], dfKde[yAxis], shade=False, cbar=True, cmap="inferno_r", levels = 5, shade_lowest=False, ax=axSNS)
    else:
        sns.kdeplot(dfKde[xAxis], dfKde[yAxis], shade=False, cbar=True, cmap="inferno_r", levels = 10, shade_lowest=False, ax=axSNS)
    axSNS.plot(xData, yData, 'k.', markersize=3, color = "Blue")
    plt.savefig(today+"_"+xAxis+"_v_"+yAxis+"_"+name+"_contour.png", bbox_inches='tight')

    # Extract kde and write into output file
    Z = kernel(positions).T

    # Output in date_xAxis_v_yAxis format

    fid = open(today+"_"+xAxis+"_v_"+yAxis+"_kde.csv",'w')
    #for currentIndex,elem in enumerate(positions):
    for currentIndex,elem in enumerate(Z):
        s1 = '%f, %f, %f\n'%(positions[0][currentIndex], positions[1][currentIndex], Z[currentIndex] )
        #s1 = '%f, %f, %f, %f, %f, %f, %f\n'%(positions[0][currentIndex], positions[1][currentIndex], positions[2][currentIndex], positions[3][currentIndex], positions[4][currentIndex], positions[5][currentIndex], Z[currentIndex]*10000000 )
        fid.write(s1)
    fid.close()
    return Z


##############################################
#               FILE INPUT
##############################################

name = "C:\\Users\\gjowl\\Documents\\Senes Lab\\Design Research\\Sequence Design\\Analysis\\Design_files\\2021_11_02_rawDesignData.csv"
#name = "C:\\Users\\gjowl\\Documents\\Senes Lab\\Design Research\\Sequence Design\\Analysis\\Design_files\\2021_10_02_rawDesignData.csv"
#name = "C:\\Users\\gjowl\\Documents\\Senes Lab\\Design_data\\Design_files\\designsSoFar.csv"

# Gets the header line to be used for the analysis
header = pd.read_csv(name, nrows=0).columns.tolist()

#TODO: something that may be nice would be to have a way to get the names of the header inputs and choosing what to use; in case I decide not to have some of these things in future implementations of the code
df = pd.read_csv(name, sep=",")

##############################################
#           MAKE SHEETS FOR OUTPUT
##############################################
dfAll = df
dfNoIMM1 = df[df["DimerNoIMM1"] < 0]
df = df[df["VDWDiff"] < 0]
df = df.drop_duplicates(subset=['Sequence'], keep=False)
#dfBad = df[df["Total"] > 0]

dfT = df[df["Total"] < 0]
dfTH = dfT[dfT["HBONDDiff"] > -5]
df21 = df[df["Sequence"].str.len() == 21]
df24 = df[df["Sequence"].str.len() == 24]
df21neg = df21[df21["Total"] < 0]
df24neg = df24[df24["Total"] < 0]

tmp = []
for i, j in df21.iterrows():
    newSeq = j["InterfaceSeq"][4:18]
    tmp.append(newSeq)
df21["Interface"]=tmp

#TODO: add in a way to determine number of left and right handed points for geometry (without double counting)
#outputs unique number of values for each column. Since values can be picked multiple times when choosing geometry,
#number of unique geometries is greatest number of all geometries
#Just realized this also helps me with sequences: There are 10395 unique sequences according to this
df_dup = dfT[dfT.duplicated(['Sequence'], keep=False)]
print(df_dup.nunique())
print(dfT.nunique())
df_unique = dfT.drop_duplicates(subset=['Sequence'], keep=False)
print(df_unique.nunique())

#TODO: use this new dataframe for graphing
#TODO: add in a check for each sequence
#add in a way to get the membrane sequence % compared to a random sequence here
#tmp = df[df["InternalSequenceEntropy"]]
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
        ca = np.append(ca, tmp["crossingAngle"].mean())
        ax = np.append(ax, tmp["axialRotation"].mean())
        z = np.append(z, tmp["zShift"].mean())
        count = np.append(count, tmp.shape[0])
    else:
        tmp = df[df["Total"] > -30+(i*5)]
        tmp = tmp[tmp["Total"] < -30+((i+1)*5)]
        vdw = np.append(vdw, tmp["VDWDiff"].mean())
        hbond = np.append(hbond, tmp["HBONDDiff"].mean())
        imm1 = np.append(imm1, tmp["IMM1Diff"].mean())
        x = np.append(x, tmp["xShift"].mean())
        ca = np.append(ca, tmp["crossingAngle"].mean())
        ax = np.append(ax, tmp["axialRotation"].mean())
        z = np.append(z, tmp["zShift"].mean())
        count = np.append(count, tmp.shape[0])
    i+=1

dfA["VDWDifference"] = vdw
dfA["HbondDifference"] = hbond
dfA["IMM1Difference"] = imm1
dfA["xShift"] = x
dfA["crossingAngle"] = ca
dfA["axialRotation"] = ax
dfA["zShift"] = z
dfA["Count"] = count

##############################################
#          PLOT KDE OVERLAYS
##############################################
dfPath = "C:\\Users\\gjowl\\Downloads\\2020_09_23_kdeData.csv"
dfKde = pd.read_csv(dfPath)

#negative data
x = df.loc[:, "xShift"]
y = df.loc[:, "crossingAngle"]
ax1  = df.loc[:, "axialRotation"]
ax2  = df.loc[:, "axialRotation"]
z1  = df.loc[:, "zShift"]
z2  = df.loc[:, "zShift"]

#negative 21
x21neg = df21neg.loc[:, "xShift"]
y21neg = df21neg.loc[:,"crossingAngle"]

#negative right
x24neg = df24neg.loc[:, "xShift"]
y24neg = df24neg.loc[:, "crossingAngle"]

# all data
xAll  = dfAll.loc[:, "xShift"]
caAll = dfAll.loc[:, "crossingAngle"]
axAll1  = dfAll.loc[:, "axialRotation"]
axAll2  = dfAll.loc[:, "axialRotation"]
zAll1  = dfAll.loc[:, "zShift"]
zAll2  = dfAll.loc[:, "zShift"]

#VDW > 0
dfVDWPos = dfAll[dfAll["VDWDiff"] > 0]
xvdw    = dfVDWPos.loc[:, "xShift"]
yvdw    = dfVDWPos.loc[:, "crossingAngle"]
ax1vdw  = dfVDWPos.loc[:, "axialRotation"]
ax2vdw  = dfVDWPos.loc[:, "axialRotation"]
z1vdw   = dfVDWPos.loc[:, "zShift"]
z2vdw   = dfVDWPos.loc[:, "zShift"]

#Energy > 100: high clashing
dfClash = dfAll[dfAll["Total"] > 100]
xcl    = dfClash.loc[:, "xShift"]
ycl    = dfClash.loc[:, "crossingAngle"]
ax1cl  = dfClash.loc[:, "axialRotation"]
ax2cl  = dfClash.loc[:, "axialRotation"]
z1cl   = dfClash.loc[:, "zShift"]
z2cl   = dfClash.loc[:, "zShift"]

#NoIMM1< 0 AND Energy > 0
dfIMM1Energy = dfNoIMM1[dfNoIMM1["Total"] > 0]
xIMM1    = dfIMM1Energy.loc[:, "xShift"]
yIMM1    = dfIMM1Energy.loc[:, "crossingAngle"]
ax1IMM1  = dfIMM1Energy.loc[:, "axialRotation"]
ax2IMM1  = dfIMM1Energy.loc[:, "axialRotation"]
z1IMM1   = dfIMM1Energy.loc[:, "zShift"]
z2IMM1   = dfIMM1Energy.loc[:, "zShift"]

#Plot
name = "C:\\Users\\gjowl\\Downloads\\geometries.csv"
#name = "C:\\Users\\gjowl\\Documents\\Senes Lab\\Design_data\\Design_files\\designsSoFar.csv"

plotKdeOverlay(dfKde, x, y, "xShift", "crossingAngle", 1)
plotKdeOverlay(dfKde, xvdw, yvdw, "xShift", "crossingAngle", 2)
plotKdeOverlay(dfKde, xcl, ycl, "xShift", "crossingAngle", 3)
plotKdeOverlay(dfKde, xIMM1, yIMM1, "xShift", "crossingAngle", 5)
plotKdeOverlay(dfKde, xAll, caAll, "xShift", "crossingAngle", 4)
plotKdeOverlay(dfKde, x21neg, y21neg, "xShift", "crossingAngle", 6)
plotKdeOverlay(dfKde, x24neg, y24neg, "xShift", "crossingAngle", 7)
#plotKdeOverlay(dfKde, ax1, ax2, "Rot1", "Rot2", 1)
#plotKdeOverlay(dfKde, ax1vdw, ax2vdw, "Rot1", "Rot2", 2)
#plotKdeOverlay(dfKde, ax1cl, ax2cl, "Rot1", "Rot2", 3)
#plotKdeOverlay(dfKde, ax1IMM1, ax2IMM1, "Rot1", "Rot2", 5)
#plotKdeOverlay(dfKde, axAll1, axAll2, "Rot1", "Rot2", 4)
#plotKdeOverlay(dfKde, z1, z2, "Z1", "Z2", 1)
#plotKdeOverlay(dfKde, z1vdw, z2vdw, "Z1", "Z2", 2)
#plotKdeOverlay(dfKde, z1cl, z2cl, "Z1", "Z2", 3)
#plotKdeOverlay(dfKde, z1IMM1, z2IMM1, "Z1", "Z2", 5)
#plotKdeOverlay(dfKde, zAll1, zAll2, "Z1", "Z2", 4)

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
with pd.ExcelWriter('C:\\Users\\gjowl\\Documents\\Senes Lab\\Design Research\\Sequence Design\\Analysis\\Design_files\\2021_11_02_analyzedDesignData.xlsx',engine='xlsxwriter') as writer:
    dfT.to_excel(writer,sheet_name='Total Energy < 0',startrow=0 , startcol=0)
    dfNoIMM1.to_excel(writer,sheet_name='DimerNoIMM1 < 0',startrow=0 , startcol=0)
    dfTH.to_excel(writer,sheet_name='HbondDifference > -5',startrow=0 , startcol=0)
    df_dup.to_excel(writer,sheet_name='Duplicates',startrow=0 , startcol=0)
    df_unique.to_excel(writer,sheet_name='Unique',startrow=0 , startcol=0)
    dfA.to_excel(writer, sheet_name='Averages',startrow=0 , startcol=0)
    dfAll.to_excel(writer,sheet_name='allData',startrow=0 , startcol=0)
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
