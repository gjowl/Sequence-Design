# -*- coding: utf-8 -*-
"""
Created on Fri Mar  5 15:44:57 2021

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

date = input("Date in year_month_day format (2021_04_08): ")

name = input("Insert type of data to perform kde (angle_v_dist/z/rot): ")
if name == "NA":
    name = "angle_v_dist"
elif name == "":
    name = "angle_v_dist"
df = pd.read_csv("C:\\Users\\gjowl\\Downloads\\2020_02_21_"+name+"_plottingdata.csv")
#df = pd.read_csv("C:\\Users\\gjowl\\Downloads\\2021_10_11_geometryDensityFile.csv")
if name == "angle_v_dist":
    xaxis = "Distance"
    yaxis = "Angle"
    xmin = 6
    xmax = 12
    ymin = -100
    ymax = 100
elif name == "z":
    xaxis = "Z1"
    yaxis = "Z2"
    xmin = 0
    xmax = 6
    ymin = 0
    ymax = 6
elif name == "rot":
    xaxis = "Rot1"
    yaxis = "Rot2"
    xmin = 0
    xmax = 100
    ymin = 0
    ymax = 100

dist = df.loc[:, xaxis]
ang = df.loc[:, yaxis]

df2 = pd.read_excel("C:\\Users\\gjowl\\Documents\\2021_05_25_analyzedDesignData.xlsx")

df2 = df2[df2["xShift"] < 12]

#dist2 = df2.loc[:, "startXShift"]
#ang2 = df2.loc[:, "startCrossingAngle"]

#df2 = df2[df2["Total"] < 0]

#dist2 = df2.loc[:, "startXShift"]
#ang2 = df2.loc[:, "startCrossingAngle"]

#distNeg = df2.loc[:, "xShift"]
#angNeg = df2.loc[:, "crossingAngle"]

##############################################
#         KERNEL DENSITY CALCULATION
##############################################
if xaxis == "Distance":
    X, Y = np.mgrid[xmin:xmax:24j, ymin:ymax:40j]
elif xaxis == "Z1":
    X, Y = np.mgrid[xmin:xmax:20j, ymin:ymax:20j]
elif xaxis == "Rot1":
    X, Y = np.mgrid[xmin:xmax:20j, ymin:ymax:20j]
positions = np.vstack([X.ravel(), Y.ravel()])
values = np.vstack([dist, ang])
kernel = stats.gaussian_kde(values)
kernel.set_bandwidth(bw_method='silverman')
print(kernel.covariance_factor())
Z = np.reshape(kernel(positions).T, X.shape)

##############################################
#            PLOT KERNEL DENSITY
##############################################
#fig, ax = plt.subplots(1, 1, figsize=(1,800))
fig, ax = plt.subplots()
plt.grid(True)
plt.xlabel(xaxis)
plt.ylabel(yaxis)
plt.title('All')
ax.use_sticky_edges = False
q = ax.imshow(np.rot90(Z), cmap=plt.cm.gist_earth_r,
          extent=[xmin, xmax, ymin, ymax], aspect="auto")
#ax.plot(dist, ang, 'k.', markersize=2)
#ax.plot(dist2, ang2, 'k.', markersize=2, color = "Black")
#ax.plot(distNeg, angNeg, 'k.', markersize=4, color = "Red")
#ax.margins(x=2, y=2)
ax.set_ylim([ymin, ymax])
#ax.set_aspect(0.5)
if xaxis == "Distance":
    ax.set_xlim([6, 12])
    ax.set_xticks([6,7,8,9,10,11,12])
#ax.legend(loc='upper left')
axes = plt.gca()
print(axes)
plt.colorbar(q)
plt.savefig(date+"_"+xaxis+"_v_"+yaxis+".pdf", bbox_inches='tight')
plt.show()

fid = open(date+"_"+name+'_kde.csv','w')
Z1 = (kernel(positions).T, X.shape)
Z = kernel(positions).T
#for currentIndex,elem in enumerate(positions):
for currentIndex,elem in enumerate(Z):
  #if Z1[currentIneex]>0:
  s1 = '%f, %f, %f\n'%(positions[0][currentIndex], positions[1][currentIndex], Z[currentIndex] )
  #s1 = '%f, %f, %f, %f, %f, %f, %f\n'%(positions[0][currentIndex], positions[1][currentIndex], positions[2][currentIndex], positions[3][currentIndex], positions[4][currentIndex], positions[5][currentIndex], Z[currentIndex] )
  fid.write(s1)
fid.close()

#kde = stats.gaussian_kde(values)
#density = kde(values)

#fig, ax = plt.subplots(subplot_kw=dict(projection='3d'))
#x, y = values
#ax.scatter(x, y, c=density)
#plt.show()

#x=np.array([1, 2, 3, 4, 5])

# making subplots
#fig, ax = plt.subplots(2, 2)

# set data with subplots and plot
#ax[0, 0].plot(x, x)
#ax[0, 1].plot(x, x*2)
#ax[1, 0].plot(x, x*x)
#ax[1, 1].plot(x, x*x*x)

# set the spacing between subplots
#plt.show()

#Contour plot (imshow causes it to squeeze the image)
#fig = plt.figure()
#ax = fig.gca()
#ax.set_xlim(xmin, xmax)
#ax.set_ylim(ymin, ymax)
# Contourf plot
#cfset = ax.contourf(X, Y, Z, cmap='Blues')
## Or kernel density estimate plot instead of the contourf plot
#ax.imshow(np.rot90(Z), cmap='Blues', extent=[xmin, xmax, ymin, ymax])
# Contour plot
#cset = ax.contour(X, Y, Z, colors='k')
# Label plot
#ax.clabel(cset, inline=1, fontsize=10)
#ax.set_xlabel('Distance')
#ax.set_ylabel('Angle')
