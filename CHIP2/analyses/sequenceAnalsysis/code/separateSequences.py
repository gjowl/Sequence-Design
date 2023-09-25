import os, sys, pandas as pd, matplotlib.pyplot as plt, numpy as np

def getAADistances(input_df, aas):
    output_df = pd.DataFrame()
    for num in input_df['NumTypeAAs'].unique():
        df_tmp = input_df[input_df['NumTypeAAs'] == num].copy()
        if num > 1:
            # get the indices of all of the hbond aas
            df_tmp['AAIndices'] = df_tmp['Sequence'].apply(lambda x: [i for i, aa in enumerate(x) if aa in aas])
            # get the smallest difference within the list
            df_tmp['ShortestDistance'] = df_tmp['AAIndices'].apply(lambda x: min([x[i+1] - x[i] for i in range(len(x)-1)]))
            # get the largest difference within the list
            df_tmp['LongestDistance'] = df_tmp['AAIndices'].apply(lambda x: max([x[i+1] - x[i] for i in range(len(x)-1)]))
        else:
            df_tmp['FirstAA'] = df_tmp['Sequence'].apply(lambda x: [aa for aa in x if aa in aas][0])
            df_tmp['LongestDistance'] = 0
            df_tmp['ShortestDistance'] = 0
        output_df = pd.concat([output_df, df_tmp])
    return output_df 

# get the average percent GpA
def printPercentGpA(df):
    # keep only greater than 4 shortest distances
    df_long = df[df['ShortestDistance'] > 4]
    df_short = df[df['ShortestDistance'] <= 4]
    print('long:', len(df_long))
    # get the average percent GpA
    averageGpA = df_long['PercentGpA'].mean()
    print(f'Average percent GpA: {averageGpA}')
    # get highest percent GpA
    maxGpA = df_long['PercentGpA'].max()
    print(f'Max percent GpA: {maxGpA}')
    minGpA = df_long['PercentGpA'].min()
    print(f'Min percent GpA: {minGpA}')
    print('short:', len(df_short))
    # get the average percent GpA
    averageGpA = df_short['PercentGpA'].mean()
    print(f'Average percent GpA: {averageGpA}')
    # get highest percent GpA
    maxGpA = df_short['PercentGpA'].max()
    print(f'Max percent GpA: {maxGpA}')
    minGpA = df_short['PercentGpA'].min()
    print(f'Min percent GpA: {minGpA}')

# read command line arguments
sequenceFile = sys.argv[1]
outputDir = sys.argv[2]
os.makedirs(outputDir, exist_ok=True)

# read in the data files
df_sequence = pd.read_csv(sequenceFile)

# sequence division
hbond_aas = ['S', 'T', 'G']
ring_aas = ['W', 'Y', 'F']

# keep only the sequences with the desired amino acids
df_hbond = df_sequence[df_sequence['Sequence'].str.contains('|'.join(hbond_aas))]
df_ring = df_sequence[df_sequence['Sequence'].str.contains('|'.join(ring_aas))]
df_nonhbond = df_sequence[~df_sequence['Sequence'].str.contains('|'.join(hbond_aas))]
df_nonring = df_sequence[~df_sequence['Sequence'].str.contains('|'.join(ring_aas))]

# add labels
df_hbond['Type'] = 'HBond'
df_ring['Type'] = 'Ring'
df_nonhbond['Type'] = 'Rest'
df_nonring['Type'] = 'Rest'

# separate sequences by number of hbond aas
df_hbond['NumTypeAAs'] = df_hbond['Sequence'].apply(lambda x: len([aa for aa in x if aa in hbond_aas]))
df_ring['NumTypeAAs'] = df_ring['Sequence'].apply(lambda x: len([aa for aa in x if aa in ring_aas]))

output_df = getAADistances(df_hbond, hbond_aas)
print('ShortestDistance')
df = pd.DataFrame()
for dist in output_df['ShortestDistance'].unique():
    df_tmp = output_df[output_df['ShortestDistance'] == dist]
    #print(dist, len(df_tmp))
    #outputFile = f'numHBondAAs{dist}'
    #df_tmp.to_csv(f'{outputDir}/{outputFile}.csv', index=False)
    df = pd.concat([df, df_tmp])

# remove all sequences with G
df = df[~df['Sequence'].str.contains('G')]
print('HBond')
printPercentGpA(df)
for num in df_hbond['NumTypeAAs'].unique():
    df_tmp = df_hbond[df_hbond['NumTypeAAs'] == num]
    # get the average percent GpA
    averageGpA = df_tmp['PercentGpA'].mean()
    print(num, len(df_tmp), averageGpA)

output_df = getAADistances(df_ring, ring_aas)
df = pd.DataFrame()
for dist in output_df['ShortestDistance'].unique():
    df_tmp = output_df[output_df['ShortestDistance'] == dist]
    #print(dist, len(df_tmp))
    #outputFile = f'numHBondAAs{dist}'
    #df_tmp.to_csv(f'{outputDir}/{outputFile}.csv', index=False)
    df = pd.concat([df, df_tmp])
df = df[~df['Sequence'].str.contains('G')]
print('Ring')
printPercentGpA(df)

for num in df_ring['NumTypeAAs'].unique():
    df_tmp = df_ring[df_ring['NumTypeAAs'] == num]
    # get the average percent GpA
    averageGpA = df_tmp['PercentGpA'].mean()
    print(num, len(df_tmp), averageGpA)

# TODO: look at individual numbers of hbond aas percent gpa averages; if they are all similar, then it's likely that the hbond aas are not actually hbonding

# combine the dataframes
output_df = pd.concat([df_hbond, df_rest])
output_df.to_csv(f'{outputDir}/hbond_vs_rest.csv', index=False)
# TODO: keep thinking of how to look at this data; I've currently have 41 sequences that aren't likely to hbond by an arbitrary criteria of farther than 4 AAs; maybe look at some 
# structures to see if it's actually possible for hbonding to occur at that distance? or search what the main possible distance for hydrogen bonding is
