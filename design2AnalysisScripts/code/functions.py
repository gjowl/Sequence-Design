import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

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
def plotEnergyDiffStackedBarGraph(df, filename):
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
    p1 = plt.bar(x, VDWDiff, width, color='b')
    p2 = plt.bar(x, HBONDDiff, width, color='r', bottom=VDWDiff)
    #p3 = plt.bar(x, IMM1DimerMonomerDiff, width, color='g', bottom=HBONDDimerMonomerDiff)
    # change the dpi to make the image smaller
    fig.set_dpi(2000)
    plt.ylabel('Energy')
    plt.title('Energy Plot')
    plt.xticks(x, df['Sequence'])
    plt.ylim(-80,-30)
    plt.yticks(np.arange(-80, -30, 10))
    plt.legend((p2[0], p1[0]), ('HBOND', 'VDW'))
    #plt.show()
    # save plot
    fig.savefig(os.getcwd()+'/energyPlot_'+filename+'.png')
