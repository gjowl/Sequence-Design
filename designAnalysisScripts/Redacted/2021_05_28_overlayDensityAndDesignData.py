# -*- coding: utf-8 -*-
"""
Created on Wed Jun  2 14:05:09 2021

@author: gjowl
"""

from scipy import stats
from matplotlib import gridspec
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

##############################################
#          HOUSEKEEPING VARIABLES
##############################################

date = input("Date in year_month_day format (2021_05_28): ")

df = pd.read_csv("C:\\Users\\gjowl\\Downloads\\2020_02_21_angle_v_dist_plottingdata.csv")
xaxis = "Distance"
yaxis = "Angle"
xmin = 6
xmax = 12
ymin = -100
ymax = 100
dist = df.loc[:, xaxis]
ang = df.loc[:, yaxis]

dfRot = pd.read_csv("C:\\Users\\gjowl\\Downloads\\2020_02_21_rot_plottingdata.csv")
arxaxis = "Rot1"
aryaxis = "Rot2"
arxmin = 0
arxmax = 100
arymin = 0
arymax = 100
ar1 = dfRot.loc[:, arxaxis]
ar2 = dfRot.loc[:, aryaxis]

dfZ = pd.read_csv("C:\\Users\\gjowl\\Downloads\\2020_02_21_z_plottingdata.csv")
zxaxis = "Z1"
zyaxis = "Z2"
zxmin = 0
zxmax = 6
zymin = 0
zymax = 6
z1 = dfZ.loc[:, zxaxis]
z2 = dfZ.loc[:, zyaxis]

df2 = pd.read_excel("C:\\Users\\gjowl\\Documents\\"+date+"_analyzedDesignData.xlsx")

df2 = df2[df2["xShift"] < 12]

distStart = df2.loc[:, "startXShift"]
angStart = df2.loc[:, "startCrossingAngle"]
arStart = df2.loc[:, "startAxialRotation"]
zStart = df2.loc[:, "startZShift"]

distAll = df2.loc[:, "xShift"]
angAll = df2.loc[:, "crossingAngle"]
arAll = df2.loc[:, "axialRotation"]
zAll = df2.loc[:, "zShift"]

df2 = df2[df2["Total"] < 0]

distStartNeg = df2.loc[:, "startXShift"]
angStartNeg = df2.loc[:, "startCrossingAngle"]
arStartNeg = df2.loc[:, "startAxialRotation"]
zStartNeg = df2.loc[:, "startZShift"]

distNeg = df2.loc[:, "xShift"]
angNeg = df2.loc[:, "crossingAngle"]
arNeg = df2.loc[:, "axialRotation"]
zNeg = df2.loc[:, "zShift"]

##############################################
#         KERNEL DENSITY CALCULATION
##############################################

X, Y = np.mgrid[xmin:xmax:24j, ymin:ymax:40j]
positions = np.vstack([X.ravel(), Y.ravel()])
values = np.vstack([dist, ang])
kernel = stats.gaussian_kde(values)
kernel.set_bandwidth(bw_method='silverman')
Z = np.reshape(kernel(positions).T, X.shape)

zX, zY = np.mgrid[zxmin:zxmax:20j, zymin:zymax:20j]
positions = np.vstack([zX.ravel(), zY.ravel()])
values = np.vstack([z1, z2])
kernel = stats.gaussian_kde(values)
kernel.set_bandwidth(bw_method='silverman')
zZ = np.reshape(kernel(positions).T, zX.shape)

arX, arY = np.mgrid[arxmin:arxmax:20j, arymin:arymax:20j]
positions = np.vstack([arX.ravel(), arY.ravel()])
values = np.vstack([ar1, ar2])
kernel = stats.gaussian_kde(values)
kernel.set_bandwidth(bw_method='silverman')
arZ = np.reshape(kernel(positions).T, arX.shape)

##############################################
#            PLOT KERNEL DENSITY
##############################################
#Angle and Distance
fig, ax = plt.subplots()
plt.grid(True)
plt.xlabel(xaxis+" (Å)")
plt.ylabel(yaxis+" (°)")
#plt.title('Density')
ax.use_sticky_edges = False
q = ax.imshow(np.rot90(Z), cmap=plt.cm.gist_earth_r,
          extent=[xmin, xmax, ymin, ymax], aspect="auto")
ax.plot(distStartNeg, angStartNeg, 'k.', markersize=2, color = "Black")
ax.plot(distNeg, angNeg, 'k.', markersize=4, color = "Red")
ax.set_ylim([ymin, ymax])
ax.set_xlim([xmin, xmax])
ax.set_xticks([6,7,8,9,10,11,12])
axes = plt.gca()
print(axes)
#plt.colorbar(q)
plt.savefig(date+"_angdistDensityDesignOverlay.pdf", bbox_inches='tight')
plt.show()

#Angle and Distance
fig, ax = plt.subplots()
plt.grid(True)
plt.xlabel(xaxis+" (Å)")
plt.ylabel(yaxis+" (°)")
#plt.title('Density')
ax.use_sticky_edges = False
q = ax.imshow(np.rot90(Z), cmap=plt.cm.gist_earth_r,
          extent=[xmin, xmax, ymin, ymax], aspect="auto")
ax.plot(distAll, angAll, 'k.', markersize=3, color = "Black")
ax.plot(distNeg, angNeg, 'k.', markersize=3, color = "Red")
ax.set_ylim([ymin, ymax])
ax.set_xlim([xmin, xmax])
ax.set_xticks([6,7,8,9,10,11,12])
axes = plt.gca()
print(axes)
#plt.colorbar(q)
plt.savefig(date+"_angdistDensityDesignOverlay.pdf", bbox_inches='tight')
plt.show()

#Rotation
fig, ax = plt.subplots()
plt.grid(True)
plt.xlabel(arxaxis)
plt.ylabel(aryaxis)
#plt.title('Density')
ax.use_sticky_edges = False
q = ax.imshow(np.rot90(arZ), cmap=plt.cm.gist_earth_r,
          extent=[arxmin, arxmax, arymin, arymax], aspect="auto")
ax.plot(arStartNeg, arStartNeg, 'k.', markersize=3, color = "Black")
ax.plot(arNeg, arNeg, 'k.', markersize=3, color = "Red")
ax.set_ylim([arymin, arymax])
ax.set_xlim([arxmin, arxmax])
ax.set_xticks([0,20,40,60,80,100])
axes = plt.gca()
print(axes)
#plt.colorbar(q)
plt.savefig(date+"_zDensityDesignOverlay.pdf", bbox_inches='tight')
plt.show()

#Z
fig, ax = plt.subplots()
plt.grid(True)
plt.xlabel(zxaxis)
plt.ylabel(zyaxis)
#plt.title('Density')
ax.use_sticky_edges = False
q = ax.imshow(np.rot90(zZ), cmap=plt.cm.gist_earth_r,
          extent=[zxmin, zxmax, zymin, zymax], aspect="auto")
ax.plot(zStartNeg, zStartNeg, 'k.', markersize=3, color = "Black")
ax.plot(zNeg, zNeg, 'k.', markersize=3, color = "Red")
ax.set_ylim([zymin, zymax])
ax.set_xlim([zxmin, zxmax])
ax.set_xticks([0,1,2,3,4,5,6])
axes = plt.gca()
print(axes)
#plt.colorbar(q)
plt.savefig(date+"_rotDensityDesignOverlay.pdf", bbox_inches='tight')
plt.show()
