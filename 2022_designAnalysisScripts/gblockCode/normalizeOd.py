import pandas as pd
import numpy as np
import os
import sys
from datetime import date

# get the date
today = date.today()

# get the csv file from the command line
csvFile = sys.argv[1]

# read csv file with OD600 values
df = pd.read_csv(csvFile, sep=',', header=0)
print(df)

# get the lowest OD600 value
lowest = df['OD600'].min()

# normalize the OD600 values to the lowest value
df['Normalize'] = df['OD600'] / lowest

# set the amount of uL to add to each well
wellVolume = 350

# normalize the OD600 values to the lowest value by dividing well volume by the normalized value
df['Cell Volume'] = wellVolume / df['Normalize'] 
df['Cell Volume'] = df['Cell Volume'].round(2)
df['Water Volume'] = wellVolume - df['Cell Volume']
df['Water Volume'] = df['Water Volume'].round(2)

# output the df to a csv file
df.to_csv(str(today)+'_normalizedOd.csv', sep='\t')