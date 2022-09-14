import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from matplotlib.ticker import PercentFormatter
from matplotlib.ticker import PercentFormatter
from matplotlib.ticker import PercentFormatter
from matplotlib.ticker import PercentFormatter

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
def plotEnergyDiffStackedBarGraph(df, outputDir):
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
    p1 = plt.bar(x, VDWDiff, width, color='cornflowerblue', edgecolor='black')
    p2 = plt.bar(x, HBONDDiff, width, color='firebrick', bottom=VDWDiff, edgecolor='black')
    #p3 = plt.bar(x, IMM1DimerMonomerDiff, width, color='g', bottom=HBONDDimerMonomerDiff)
    # change the dpi to make the image smaller
    fig.set_dpi(2000)
    plt.ylabel('Energy')
    plt.title('Energy Plot')
    plt.xticks(x, df['Sequence'])
    plt.yticks(np.arange(-70, 0, 10))
    plt.ylim(-90,-35)
    plt.yticks(np.arange(-90, -30, 10))
    plt.legend((p2[0], p1[0]), ('HBOND', 'VDW'))
    # save the number of designs on the plot
    # output the number of sequences in the dataset onto plot top left corner
    plt.text(0.2, -33, 'N = '+str(n))
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