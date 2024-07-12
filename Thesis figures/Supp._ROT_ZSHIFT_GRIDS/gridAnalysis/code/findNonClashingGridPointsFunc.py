import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
import seaborn as sns
import os
import random as rand

def getNonClashingGeometryData(inputDir, outputFile, columns):
    # setup output dataframe
    outputDf = pd.DataFrame(columns=columns)
    # loop through the files in the input directory
    for file in os.listdir(inputDir):
        # check to see if the file is a pdb file
        if file.endswith('.pdb'):
            # remove the .pdb extension
            file = file[:-4]
            # split file by "_"
            splitFile = file.split('_')
            # get xShift, crossingAngle, axialRotation, zShift, and energy
            xShift, crossingAngle, axialRotation, zShift, energy = splitFile[0], splitFile[1], splitFile[2], splitFile[3], splitFile[4]
            # keep only numbers
            xShift = xShift.replace('x', '')
            crossingAngle = crossingAngle.replace('cross', '')
            axialRotation = axialRotation.replace('ax', '')
            zShift = zShift.replace('z', '')
            energy = energy.replace('energy', '')
            # convert to float
            xShift, crossingAngle, axialRotation, zShift, energy = float(xShift), float(crossingAngle), float(axialRotation), float(zShift), float(energy)
            # add to a dataframe
            outputDf = pd.concat([outputDf, pd.DataFrame([[xShift, crossingAngle, axialRotation, zShift, energy]], columns=columns)])
    # write the output file
    outputDf.to_csv(outputFile, index=False)

def getDfMinAndMax(df, col):
    # get the min and max of the xShift 
    min = df[col].min()
    max = df[col].max()
    # get the min and max of the column
    dfMin = df[df[col] == min]
    dfMax = df[df[col] == max]
    return dfMin, dfMax

def plotKde(df, xAxis, yAxis, xAndYDict, outputDir, title):
    # get the x and y values from the dictionary
    xMin, xMax = xAndYDict[xAxis]['min'], xAndYDict[xAxis]['max']
    yMin, yMax = xAndYDict[yAxis]['min'], xAndYDict[yAxis]['max']

    # grid the data for kde plots 
    X, Y = np.mgrid[xMin:xMax:200j, yMin:yMax:100j] # originally split x into 20 bins, y into 12 bins
    
    # round all values to 2 decimal places
    X = np.around(X, 2)
    Y = np.around(Y, 2)

    #Kernel Density Estimate Calculation
    positions = np.vstack([X.ravel(), Y.ravel()])
    x = df.loc[:, xAxis]
    y = df.loc[:, yAxis]
    values = np.vstack([x, y])
    kernel = stats.gaussian_kde(values)
    bw = 0.2
    #bw = 'silverman'
    kernel.set_bandwidth(bw_method=bw) # position to change the bandwidth of the kde
    Z = np.reshape(kernel(positions).T, X.shape)

    # Plotting code below
    fig, ax = plt.subplots()
    plt.grid(False)
    plt.xlabel(xAxis)
    plt.ylabel(yAxis)
    plt.title(title)
    ax.use_sticky_edges = False
    q = ax.imshow(np.rot90(Z), cmap=plt.cm.Blues, extent=[xMin, xMax, yMin, yMax], aspect="auto")
    ax.set_xlim([xMin, xMax])
    ax.set_ylim([yMin, yMax])
    axes = plt.gca()

    # output the number of data points on the figure
    plt.text(xMin-0.2, yMin-0.5, 'n = '+str(len(df)))

    # output the figure
    outputTitle = xAxis+"_v_"+yAxis+"_"+title
    #sns.kdeplot(x=df[xAxis], y=df[yAxis], shade=False, cbar=True, cmap="inferno_r", levels = 10, thresh=False)
    plt.savefig(outputDir+outputTitle+".png", bbox_inches='tight')
    plt.savefig(outputDir+outputTitle+".svg", bbox_inches='tight')
    Zout = kernel(positions).T
    acceptGrid = getAcceptGridCsv(Zout, positions, outputDir, outputTitle)
    plt.close()

    # make a contour plot
    fig, ax = plt.subplots()
    ax.contour(X, Y, Z, cmap='Blues')
    plt.xlabel(xAxis)
    plt.ylabel(yAxis)
    plt.title(title)
    plt.savefig(outputDir+outputTitle+"_contour.png", bbox_inches='tight')
    plt.savefig(outputDir+outputTitle+"_contour.svg", bbox_inches='tight')
    plt.close()
    return Z, acceptGrid

# for a reason I haven't figured out yet, this kde code slightly changes the grid points, but the image looks correct
# the values are similar regardless, so I'm converting it to the right grid points below
def getAcceptGridCsv(Z, positions, outputDir, outputTitle):
    outputDf = pd.DataFrame()
    # turn z into a percentage
    zMax = Z.max()
    Z = Z/zMax
    # round all values to 2 decimal places
    Z = np.around(Z, 2)
    # Output the density data for each geometry
    for currentIndex,elem in enumerate(Z):
        s1 = '%f, %f, %f\n'%(positions[0][currentIndex], positions[1][currentIndex], Z[currentIndex] )
        # add to the dataframe
        outputDf = pd.concat([outputDf, pd.DataFrame([[positions[0][currentIndex], positions[1][currentIndex], Z[currentIndex]]], columns=['x', 'y', 'z'])])
    return outputDf

def plotKdeOverlay(kdeZScores, xAxis, xmin, xmax, yAxis, ymin, ymax, data, dataColumn, outputDir, outputTitle):
    # Plotting code below
    fig, ax = plt.subplots()
    # plotting labels and variables 
    plt.grid(False)
    plt.xlabel("Axial Rot")
    plt.ylabel("Z")
    plt.title(dataColumn)
    # Setup for plotting output
    plt.rc('font', size=10)
    plt.rc('xtick', labelsize=10)
    plt.rc('ytick', labelsize=10)

    # setup kde plot for original geometry dataset
    ax.use_sticky_edges = False
    q = ax.imshow(np.rot90(kdeZScores), cmap=plt.cm.Blues,
        extent=[xmin, xmax, ymin, ymax], aspect="auto")
    ax.set_xlim([xmin, xmax])
    ax.set_ylim([ymin, ymax])
    
    # Plot datapoints onto the graph with fluorescence as size
    # get colormap shades of green
    cmap = plt.cm.Reds
    cmap = cmap.reversed()

    # get min and max of the data
    min_val = np.min(data)
    max_val = np.max(data)
    
    # flip the data so that the min is at the top of the colorbar
    norm = matplotlib.colors.Normalize(vmin=-15, vmax=10) # TODO: change this to the min and max of the data
    ax.scatter(xAxis, yAxis, c=cmap(norm(data)), s=30, alpha=0.5)
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)

    # normalize the fluorescent data to the range of the colorbar
    sm.set_array([])  # only needed for matplotlib < 3.1
    fig.colorbar(sm)
    # add the number of datapoints to the plot
    plt.text(xmin-0.2, ymin-0.5, "# Geometries = " + str(len(xAxis)), fontsize=10)
    axes = plt.gca()

    #plt.colorbar(q)
    # output the number of sequences in the dataset onto plot
    plt.savefig(outputDir+"/"+outputTitle+"_kdeOverlay.png", bbox_inches='tight', dpi=150)
    plt.close()

# loops through all of the geometry grids output from the kde function and  
def getRandomGeometryDf(geomGrid, numGeometries, acceptCutoff, geometryDict, cols):
    # remove geometries with density less than the cutoff
    geomGrid = geomGrid[geomGrid['density'] >= acceptCutoff]
    # pick x random geometries from the acceptGrid
    randRows = geomGrid.sample(n=numGeometries)
    # initialize the dictionary
    randGeomDict = {}
    # loop through the rangome rows in the randRows dataframe
    for col in cols:
        geoms = []
        for index, row in randRows.iterrows():
            if col != "density":
                # get the geometry for the column from the dataRow
                geometry = row[col]
                # get a random geometry for the current column
                randomGeom = getRandomGeom(col, geometryDict, geometry)
                # add the geometry to the list of geometries
                geoms.append(randomGeom)
            else:
                # get the geometry for the column from the dataRow
                density = row[col]
                # add the geometry to the list of geometries
                geoms.append(density)
        # add the geometry to a dictionary
        geometryDict[col] = geoms
    # convert the dictionary to a dataframe
    randomGeomGrid = pd.DataFrame.from_dict(geometryDict)
    return randomGeomGrid

# gets a random geometry from a given row of data for a given column
def getRandomGeom(col, geometryDict, geometry):
    # get the min, max, and inc for the geometry from the dictionary
    colMin = geometryDict[col]['min']
    colMax = geometryDict[col]['max']
    inc = geometryDict[col]['inc']
    # get random float between -inc and inc
    randFloat = rand.uniform(-inc, inc)
    # add the random float to the geometry value
    randGeom = geometry + randFloat
    # check if the randGeom is less than the colMin
    if randGeom < colMin:
        # set randGeom to colMin
        randGeom = colMin
    # check if the randGeom is greater than the colMax
    elif randGeom > colMax:
        # set randGeom to colMax
        randGeom = colMax
    # return the randGeom
    return randGeom