import os, sys, pandas as pd

# read in the data file
df = pd.read_csv(sys.argv[1], sep=',')

# get the duplicate sequences
df_duplicates = df[df.duplicated(subset=['Sequence'], keep=False)]

print(df_duplicates)