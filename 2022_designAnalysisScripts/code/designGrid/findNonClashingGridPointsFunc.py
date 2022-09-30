import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

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

def plotKde(df, xAxis, yAxis, xAndYDict, accceptCutoff, outputDir, title):
    # get the x and y values from the dictionary
    xMin, xMax = xAndYDict[xAxis]['min'], xAndYDict[xAxis]['max']
    yMin, yMax = xAndYDict[yAxis]['min'], xAndYDict[yAxis]['max']

    # grid the data for kde plots (split x into 20 bins, y into 12 bins)
    X, Y = np.mgrid[xMin:xMax:21j, yMin:yMax:13j]
    
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
    kernel.set_bandwidth(bw_method=bw) # position to change the bandwidth of the kde
    Z = np.reshape(kernel(positions).T, X.shape)

    # Plotting code below
    fig, ax = plt.subplots()
    plt.grid(False)
    plt.xlabel(xAxis)
    plt.ylabel(yAxis)
    plt.title(title)
    ax.use_sticky_edges = False
    q = ax.imshow(np.rot90(Z), cmap=plt.cm.Blues,
        extent=[xMin, xMax, yMin, yMax], aspect="auto")
    ax.set_xlim([xMin, xMax])
    ax.set_ylim([yMin, yMax])
    axes = plt.gca()

    # output the number of data points on the figure
    plt.text(xMin-0.2, yMin-0.5, 'n = '+str(len(df)))

    # output the figure
    outputTitle = xAxis+"_v_"+yAxis+"_"+title
    sns.kdeplot(x=df[xAxis], y=df[yAxis], shade=False, cbar=True, cmap="inferno_r", levels = 10, thresh=False)
    plt.savefig(outputDir+outputTitle+".png", bbox_inches='tight')
    
    Zout = kernel(positions).T
    acceptGrid = getAcceptGridCsv(Zout, positions, outputDir, outputTitle, acceptCutoff)
    return Z, acceptGrid

# for a reason I haven't figured out yet, this kde code slightly changes the grid points, but the image looks correct
# the values are similar regardless, so I'm converting it to the right grid points below
def getAcceptGridCsv(Z, positions, outputDir, outputTitle, acceptCutoff):
    # turn z into a percentage
    zMax = Z.max()
    Z = Z/zMax
    # round all values to 2 decimal places
    Z = np.around(Z, 2)
    print(Z)
    # remove all values below the cutoff
    Z[Z < acceptCutoff] = 0
    print(Z)
    exit()
    # Output the density data for each geometry
    fid = open(outputDir+outputTitle+"test.csv",'w')
    for currentIndex,elem in enumerate(Z):
        s1 = '%f, %f, %f\n'%(positions[0][currentIndex], positions[1][currentIndex], Z[currentIndex] )
        fid.write(s1)
    fid.close()
    return Z

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
