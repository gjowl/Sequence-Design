import os, sys, pandas as pd, numpy as np, matplotlib.pyplot as plt

# read in the command line arguments
sequenceFile = sys.argv[1]
outputDir = sys.argv[2]

# make the output directory if it doesn't exist
os.makedirs(name=outputDir, exist_ok=True)

# read in the sequence file
df = pd.read_csv(sequenceFile)

# keep only the sequences that have PercentGpA > 0.5
df = df[df['PercentGpA'] > 0.5]

# define the aas to track
hbond_aas = ['T', 'S']
ring_aas = ['W', 'Y', 'F']

# loop through the dataframe 
for seq in df['Sequence'].unique():
    # count the number of hbond and ring aas
    hbond_count = 0
    ring_count = 0
    for aa in seq:
        if aa in hbond_aas:
            hbond_count += 1
        elif aa in ring_aas:
            ring_count += 1
    # add the counts to the dataframe
    df.loc[df['Sequence'] == seq, 'hbond_count'] = hbond_count
    df.loc[df['Sequence'] == seq, 'ring_count'] = ring_count
    total_count = hbond_count + ring_count
    df.loc[df['Sequence'] == seq, 'total_count'] = total_count
    ratio = hbond_count / total_count 
    df.loc[df['Sequence'] == seq, 'ratio'] = ratio

# keep only unique sequences
df = df.drop_duplicates(subset=['Sequence'])

# save the dataframe
for sample in df['Sample'].unique():
    sample_df = df[df['Sample'] == sample]
    sample_df.to_csv(f'{outputDir}/{sample}_hbond_ring_counts.csv', index=False)
    # group the sequences by the number of hbond and ring aas
    grouped_df = sample_df.groupby(['hbond_count', 'ring_count']).count().reset_index()
    # plot the data
    plt.scatter(grouped_df['hbond_count'], grouped_df['ring_count'], s=grouped_df['total_count']*1000, c=grouped_df['total_count'], cmap='viridis')
    plt.xlabel('Number of Hydrogen Bonding Amino Acids')
    plt.ylabel('Number of Ring Amino Acids')
    plt.title(f'{sample} Hydrogen Bonding and Ring Amino Acid Counts')
    plt.colorbar(label='Number of Sequences')
    # set the axes to be separated by 1
    min_ring = grouped_df['ring_count'].min()
    max_ring = grouped_df['ring_count'].max()
    plt.xticks(np.arange(0, 4, 1))
    plt.yticks(np.arange(0, 4, 1))
    plt.savefig(f'{outputDir}/{sample}_hbond_ring_counts.png')
    plt.close()

df.to_csv(f'{outputDir}/hbond_ring_counts.csv', index=False)
