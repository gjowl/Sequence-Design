import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
=======
from matplotlib.ticker import PercentFormatter
>>>>>>> ad76af7087793a7c3c58fcc8c653ea5605f2b2ff
=======
from matplotlib.ticker import PercentFormatter
>>>>>>> ad76af7087793a7c3c58fcc8c653ea5605f2b2ff
=======
from matplotlib.ticker import PercentFormatter
>>>>>>> ad76af7087793a7c3c58fcc8c653ea5605f2b2ff
=======
from matplotlib.ticker import PercentFormatter
>>>>>>> 526550a3041fc0669e9d118b0c727dbcc999064b
=======
from matplotlib.ticker import PercentFormatter
>>>>>>> aff5e515ed04cfd4d742cd0dd2b778f297359cb8

def getEnergyDiff(df_designs, df_energy, energy):
    list_energyDiff = []
    dimerEnergyName = energy+'Dimer'
    monomerEnergyName = energy+'Monomer'
    # loop through the values within the Sequence column of the design file
    for index, row in df_designs.iterrows():
        # get the VDWDimer value for the sequence
        energyDimer = row[dimerEnergyName]
        # get the sequence
        sequence = row['Sequence']
        # find the sequence in the energy file
        df_energy_sequence = df_energy[df_energy['Sequence'] == sequence]
        # get the VDWMonomer value for the sequence
        energyMonomer = df_energy_sequence[monomerEnergyName].values[0]
        # get the difference between the VDWDimer and VDWMonomer values
        diff = energyDimer - energyMonomer
        # save the diff to a list
        list_energyDiff.append(diff)
    return list_energyDiff

## set up output directory
#programPath = os.path.realpath(energyFile)
#programDir, programFile = os.path.split(programPath)
#outputDir = programDir +'/'
#
## only keep sequences in the energy file that are in the data file
#df_energy = df[df['Sequence'].isin(df_designs['Sequence'])]
#
## setup the energy list for energies to output
#list_energies = ['VDW','HBOND','IMM1']
## loop through the energy list
#for energy in list_energies:
#    # get the energy difference for each sequence
#    list_energyDiff = getEnergyDiff(df_designs, df_energy, energy)
#    # add the energy difference to the data frame
#    df_designs[energy+'Dimer-'+energy+'MonomerDiff'] = list_energyDiff
#
## output the design file
#df_designs.to_csv(outputDir+'designs_with_energyDiff.csv')
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
def plotEnergyDiffStackedBarGraph(df, filename):
=======
def plotEnergyDiffStackedBarGraph(df, outputDir):
>>>>>>> ad76af7087793a7c3c58fcc8c653ea5605f2b2ff
=======
def plotEnergyDiffStackedBarGraph(df, outputDir):
>>>>>>> ad76af7087793a7c3c58fcc8c653ea5605f2b2ff
=======
def plotEnergyDiffStackedBarGraph(df, outputDir):
>>>>>>> ad76af7087793a7c3c58fcc8c653ea5605f2b2ff
=======
def plotEnergyDiffStackedBarGraph(df, outputDir):
>>>>>>> 526550a3041fc0669e9d118b0c727dbcc999064b
=======
def plotEnergyDiffStackedBarGraph(df, outputDir):
>>>>>>> aff5e515ed04cfd4d742cd0dd2b778f297359cb8
    # data columns to plot
    n = len(df)
    x = np.arange(n)
    width = 1
    # get the VDW energy difference column
    VDWDiff = df['VDWDiff']
    # get the HBOND energy difference column
    HBONDDiff = df['HBONDDiff']*-1
    # get the IMM1 energy difference column
    IMM1Diff = df['IMM1Diff']*-1
    # setup the bar plots for each energy difference
    fig, ax = plt.subplots()
<<<<<<< HEAD
    p1 = plt.bar(x, VDWDiff, width, color='b')
    p2 = plt.bar(x, HBONDDiff, width, color='r', bottom=VDWDiff)
=======
    p1 = plt.bar(x, VDWDiff, width, color='cornflowerblue', edgecolor='black')
    p2 = plt.bar(x, HBONDDiff, width, color='firebrick', bottom=VDWDiff, edgecolor='black')
>>>>>>> aff5e515ed04cfd4d742cd0dd2b778f297359cb8
    #p3 = plt.bar(x, IMM1DimerMonomerDiff, width, color='g', bottom=HBONDDimerMonomerDiff)
    # change the dpi to make the image smaller
    fig.set_dpi(2000)
    plt.ylabel('Energy')
    plt.title('Energy Plot')
<<<<<<< HEAD
    plt.xticks(x, df['Sequence'])
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
    plt.yticks(np.arange(-70, 0, 10))
=======
    plt.ylim(-80,-30)
    plt.yticks(np.arange(-80, -30, 10))
>>>>>>> 79960644233ca4e4fae65934702dc00ff55bf9de
=======
    plt.ylim(-80,-30)
    plt.yticks(np.arange(-80, -30, 10))
>>>>>>> 79960644233ca4e4fae65934702dc00ff55bf9de
=======
    plt.ylim(-80,-30)
    plt.yticks(np.arange(-80, -30, 10))
>>>>>>> 79960644233ca4e4fae65934702dc00ff55bf9de
    plt.legend((p2[0], p1[0]), ('HBOND', 'VDW'))
    #plt.show()
    # save plot
    fig.savefig(os.getcwd()+'/energyPlot_'+filename+'.png')
=======
=======
>>>>>>> ad76af7087793a7c3c58fcc8c653ea5605f2b2ff
=======
>>>>>>> ad76af7087793a7c3c58fcc8c653ea5605f2b2ff
=======
>>>>>>> 526550a3041fc0669e9d118b0c727dbcc999064b
=======
    #plt.xticks(x, df['Sequence'])
>>>>>>> aff5e515ed04cfd4d742cd0dd2b778f297359cb8
    plt.ylim(-90,-35)
    plt.yticks(np.arange(-90, -30, 10))
    plt.legend((p2[0], p1[0]), ('HBOND', 'VDW'))
    # save the number of designs on the plot
<<<<<<< HEAD
    plt.text(0.5, -25, 'Number of Designs: '+str(n))
=======
    #plt.text(0.5, -25, 'Number of Designs: '+str(n))
    # output the number of sequences in the dataset onto plot top left corner
    plt.text(0.2, -33, 'N = '+str(n))
>>>>>>> aff5e515ed04cfd4d742cd0dd2b778f297359cb8
    # save plot
    fig.savefig(outputDir+'/energyDiffPlot.png')

# plot histogram of dataframe and column
def plotHist(df, column, outputDir, title):
    # Plotting code below
    fig, ax = plt.subplots()
    # get the minimum and maximum values of the column
    ax.hist(df[column], weights=np.ones(len(df))/len(df), bins=[-55,-50,-45,-40,-35,-30,-25,-20,-15,-10,-5], color='b')
    # set y axis to percent
    plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
    # set the y axis label
    plt.ylabel('Frequency')
    # set the x axis label
    plt.xlabel('Energy Score')
    # set the title
    plt.title(title+' histogram')
    # save the number of data points on the figure
    plt.text(-60, -0.05, 'n = '+str(len(df)))
    # check if Top in outputDir
    if 'Top' in outputDir:
        # set the y axis limits
        plt.ylim(0,0.7)
    else:
        # set the y axis limits
        plt.ylim(0,0.5)
    # save the figure
    plt.savefig(outputDir+"/histogram.png", bbox_inches='tight', dpi=150)
    plt.close()

def breakIntoDesignRegions(df):
    # divide data into dataframes for each region
    df_right = df[(df['crossingAngle'] < 0) & (df['xShift'] > 7.5)]
    df_left = df[df['crossingAngle'] > 0]
    df_gasright = df[(df['crossingAngle'] < 0) & (df['xShift'] < 7.5)]
    return df_right, df_left, df_gasright
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
>>>>>>> ad76af7087793a7c3c58fcc8c653ea5605f2b2ff
=======
>>>>>>> ad76af7087793a7c3c58fcc8c653ea5605f2b2ff
=======
>>>>>>> ad76af7087793a7c3c58fcc8c653ea5605f2b2ff
=======
>>>>>>> 526550a3041fc0669e9d118b0c727dbcc999064b
=======
>>>>>>> aff5e515ed04cfd4d742cd0dd2b778f297359cb8
