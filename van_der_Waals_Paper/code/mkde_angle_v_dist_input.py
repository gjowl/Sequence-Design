# -*- coding: utf-8 -*-
"""
Created on Fri Mar  5 15:44:57 2021

@author: gjowl
"""
import sys, os, numpy as np, pandas as pd, matplotlib.pyplot as plt, argparse
from scipy import stats
from matplotlib import gridspec 

# initialize the parser
parser = argparse.ArgumentParser(description='Plots the KDE of Angle vs Distance')

# add the necessary arguments
parser.add_argument('-inFile','--inputFile', type=str, help='the input csv file')
# add the optional arguments
parser.add_argument('-outFile','--outputFile', type=str, help='the output csv file')
parser.add_argument('-outDir','--outputDir', type=str, help='the output directory')

# extract the arguments into variables
args = parser.parse_args()
inputFile = args.inputFile
# default values for the optional arguments
outputFile = 'ang_v_dist'
outputDir = os.getcwd()

# if the optional arguments are not specified, use the default values
if args.outputFile is not None:
    outputFile = args.outputFile
if args.outputDir is not None:
    outputDir = args.outputDir
    os.mkdir(outputDir, exist_ok=True)

if __name__ == '__main__':
    # read in the command line arguments
    input_file = sys.argv[1] # 2020_02_21_plottingdata.csv
    df = pd.read_csv(input_file) 

    # set the bounds for the plot
    xmin = 6
    xmax = 12
    ymin = -100
    ymax = 100

    # rid of any data that is outside of the bounds
    df = df[df.Distance >= xmin]
    df = df[df.Distance <= xmax]
    df = df[df.Angle >= ymin]
    df = df[df.Angle <= ymax]

    ang = df.loc[:, "Angle"]
    dist = df.loc[:, "Distance"]

    # kernel density estimation calculation
    X, Y = np.mgrid[xmin:xmax:24j, ymin:ymax:40j]
    positions = np.vstack([X.ravel(), Y.ravel()])
    values = np.vstack([dist, ang])
    kernel = stats.gaussian_kde(values)
    kernel.set_bandwidth(bw_method='silverman')
    Z = np.reshape(kernel(positions).T, X.shape)

    # plot the data
    fig, ax = plt.subplots()
    plt.grid(True)
    plt.xlabel('Distance')
    plt.ylabel('Angle')
    plt.title('KDE of Angle vs Distance')
    ax.use_sticky_edges = False

    # use a blue color palette
    q = ax.imshow(np.rot90(Z), cmap=plt.cm.Blues,
              extent=[xmin, xmax, ymin, ymax], aspect="auto")
    ax.plot(dist, ang, 'k.', markersize=1)
    ax.set_xlim([xmin, xmax])
    ax.set_ylim([ymin, ymax])
    ax.set_xticks([6,7,8,9,10,11,12])
    axes = plt.gca()
    #plt.colorbar(q)

    # add the number of points to the plot in the upper right corner
    plt.text(11.5, 110, f'N = {len(df)}', fontsize=12, color='black', fontweight='bold')
    plt.savefig('ang_v_dist.png', bbox_inches='tight')
    plt.savefig('ang_v_dist.svg', bbox_inches='tight')
    plt.clf()

    # get the name of the input file without the extension or path
    name = input_file.split('/')[-1].split('.')[0]
    print(name)
    # write the data to a csv file
    fid = open(f'{name}.csv','w')
    Z1 = (kernel(positions).T, X.shape)
    Z = kernel(positions).T
    for currentIndex,elem in enumerate(Z):
      s1 = '%f, %f, %f\n'%(positions[0][currentIndex], positions[1][currentIndex], Z[currentIndex] )
      fid.write(s1)
    fid.close()