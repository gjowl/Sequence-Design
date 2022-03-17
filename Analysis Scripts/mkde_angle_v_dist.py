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
df = pd.read_csv("C:\\Users\\gjowl\\Downloads\\2020_02_21_plottingdata.csv")

xmin = 6
xmax = 12
ymin = -100
ymax = 100

ang = df.loc[:, "Angle"]
dist = df.loc[:, "Distance"]

##############################################
#         KERNEL DENSITY CALCULATION
##############################################
X, Y = np.mgrid[xmin:xmax:24j, ymin:ymax:40j]
positions = np.vstack([X.ravel(), Y.ravel()])
values = np.vstack([dist, ang])
kernel = stats.gaussian_kde(values)
kernel.set_bandwidth(bw_method='silverman')
Z = np.reshape(kernel(positions).T, X.shape)

##############################################
#            PLOT KERNEL DENSITY
##############################################
#fig, ax = plt.subplots(1, 1, figsize=(1,800))
fig, ax = plt.subplots()
plt.grid(True)
plt.xlabel('Distance')
plt.ylabel('Angle')
plt.title('All')
ax.use_sticky_edges = False
q = ax.imshow(np.rot90(Z), cmap=plt.cm.gist_earth_r,
          extent=[xmin, xmax, ymin, ymax], aspect="auto")
ax.plot(dist, ang, 'k.', markersize=1)
#ax.margins(x=2, y=2)
ax.set_xlim([xmin-1, xmax+1])
ax.set_ylim([ymin, ymax])
#ax.set_aspect(0.5)
ax.set_xticks([5,6,7,8,9,10,11,12,13])
ax.legend(loc='upper left')
axes = plt.gca()
print(axes)
#plt.colorbar(q)
plt.savefig('ang_v_dist.pdf', bbox_inches='tight')
plt.show()

fid = open('output_kde.csv','w')
Z1 = (kernel(positions).T, X.shape)
Z = kernel(positions).T
#for currentIndex,elem in enumerate(positions):
for currentIndex,elem in enumerate(Z):
  #if Z1[currentIneex]>0:
  s1 = '%f, %f, %f\n'%(positions[0][currentIndex], positions[1][currentIndex], Z[currentIndex] )

  fid.write(s1)
fid.close()

print(kernel.values)
evaluated = kernel.evaluate(np.linspace(values.min(), values.max(), 100))
value_space = np.linspace(values.min(), values.max())
plt.hist(values, density=True)
plt.plot(value_space, evaluated)
evaluated.sum()

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