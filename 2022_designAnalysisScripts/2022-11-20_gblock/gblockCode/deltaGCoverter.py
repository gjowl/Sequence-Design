import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# convert toxgreen to toxcat using the equation from Armstrong and Senes 2016
def greenToCatFunction(toxgreen):
    # toxgreen = 1.1(toxcat) + 3.38
    # toxcat = (toxgreen - 3.38) / 1.1
    toxcat = (toxgreen - 3.38) / 1.1
    return toxcat

# convert toxcat to fraction dimer using the equation from figure 5c in Diaz Vazquez et al. 2022
def catToFractionDimer(toxcat):
    # toxcat = 332.5(fractionDimer) + 24.9
    # fractionDimer = (toxcat - 24.9) / 332.5
    fractionDimer = (toxcat - 24.9) / 332.5
    return fractionDimer

# convert toxcat to fraction dimer using the equation from page 147 in Diaz Vazquez et al. 2022
def fractionDimerToKd(fractionDimer):
    # fractionDimer = 1-(-Kd+sqrt(Kd^2+8*Kd(chiT)))/4*chiT
    # fd = 1-(-Kd+sqrt(Kd^2+8*Kd(chiT)))/4*chiT
    # conversion below:
    # Kd = (1-fd)*4*chiT + sqrt((1-fd)^2*16*chiT^2 + 8*chiT)
    # chiT = 1.8*10^-4 from figure 5b in Diaz Vazquez et al. 2022
    chiT = 1.8*10**(-4)
    # Kd = 2chiT/fd -4chiT*fd + 2chiT * fd^2
    # check this conversion by hand
    #Kd = (1-fractionDimer)*4*1.8*10^(-4) + np.sqrt((1-fractionDimer)**2*16*1.8*10^(-4)**2 + 8*1.8*10^(-4))
    # by hand conversion
    #Kd = 2*1.8*10**(-4)/fractionDimer - 4*1.8*10**(-4)*fractionDimer + 2*1.8*10**(-4) * fractionDimer
    Kd = 2*chiT*((1+fractionDimer**2-2*fractionDimer)/fractionDimer)
    return Kd

# get the current directory
cwd = os.getcwd()

# get the csv file from the command line
inputFile = sys.argv[1]

# read in csv as a dataframe
df = pd.read_csv(inputFile, sep=',', header=0)

# convert toxgreen to toxcat
df['toxcat'] = greenToCatFunction(df['PercentGpA'])

# convert toxcat to fraction dimer
df['fractionDimer'] = catToFractionDimer(df['toxcat'])

# convert fraction dimer to Kd
df['Kd'] = fractionDimerToKd(df['fractionDimer'])

# rid of the negative Kd values
df = df[df['Kd'] > 0]

# convert Kd to deltaG
R = 0.0019872 # kcal/mol/K
#T = 298.15 # K
T = 310 # K
df['deltaG'] = np.log(df['Kd']) * R * T

# output the df to a csv file
df.to_csv(cwd+'/test.csv', sep=',')