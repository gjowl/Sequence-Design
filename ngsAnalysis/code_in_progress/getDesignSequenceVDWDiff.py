import sys
import os
import pandas as pd

"""

"""
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

# read in initial energy file from command line
energyFile = sys.argv[1]

# read in data file from command line
designFile = sys.argv[2]

# only keep the sequences that match the starting sequence (designs) in the data file
df = pd.read_csv(energyFile)
df_designs = pd.read_csv(designFile)
df_designs = df_designs[df_designs['Sequence'] == df_designs['StartSequence']]

# set up output directory
programPath = os.path.realpath(energyFile)
programDir, programFile = os.path.split(programPath)
outputDir = programDir +'/'

# only keep sequences in the energy file that are in the data file
df_energy = df[df['Sequence'].isin(df_designs['Sequence'])]

# setup the energy list for energies to output
list_energies = ['VDW','HBOND','IMM1']
# loop through the energy list
for energy in list_energies:
    # get the energy difference for each sequence
    list_energyDiff = getEnergyDiff(df_designs, df_energy, energy)
    # add the energy difference to the data frame
    df_designs[energy+'Dimer-'+energy+'MonomerDiff'] = list_energyDiff

# output the design file
df_designs.to_csv(outputDir+'designs_with_energyDiff.csv')

