import sys
import os
import pandas as pd

# get the current working directory
cwd = os.getcwd()+"/"

# read in the data from the csv file
df = pd.read_csv(sys.argv[1])
df = df[df['Total'] < 0]
df = df[df['Total'] < df['startEnergy']]
# define the columns to compare
columns = ['VDWDimer', 'VDWMonomer', 'HBONDDimer', 'HBONDMonomer', 'IMM1Dimer', 'IMM1Monomer']

# define the output dataframe
outputDf = pd.DataFrame()

# loop through every line of df
for i in range(len(df)):
    # get line i
    line = df.iloc[i]
    # get the value at column Total
    endEnergy = line['Total']
    startEnergy = line['startEnergy']
    # calculate the difference
    energyDiff = endEnergy - startEnergy
    # get the geometry number
    geometry = line['geometryNumber']
    # get the directory
    directory = line['Directory']
    # add the difference to the output dataframe using concat
    outputDf = pd.concat([outputDf,pd.DataFrame({'Dir':directory,'geometryNumber':geometry,'startEnergy':startEnergy,'endEnergy':endEnergy,'energyDiff':energyDiff},index=[0])],axis=0)

# separate the data into two dataframes by geometry number
df0 = outputDf[outputDf['geometryNumber'] == 0]
df1 = outputDf[outputDf['geometryNumber'] == 1]
df2 = outputDf[outputDf['geometryNumber'] == 2]

# get the mean of the energy differences
mean0 = df0['energyDiff'].mean()
mean1 = df1['energyDiff'].mean()
mean2 = df2['energyDiff'].mean()

print('Mean:',mean0)
print('Mean:',mean1)
print('Mean:',mean2)

# write output to csv
df0.to_csv(cwd+"energyDiff_0.csv")
df1.to_csv(cwd+"energyDiff_1.csv")
df2.to_csv(cwd+"energyDiff_2.csv")
outputDf.to_csv(cwd+"energyDiff.csv")