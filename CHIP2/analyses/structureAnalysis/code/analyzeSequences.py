import os, sys, pandas as pd, numpy as np, matplotlib.pyplot as plt

# read in the command line arguments
sequenceFile = sys.argv[1]
outputDir = sys.argv[2]

# make the output directory if it doesn't exist
os.makedirs(name=outputDir, exist_ok=True)

# read in the sequence file
df = pd.read_csv(sequenceFile)

# keep only non-duplicated sequences
df = df.drop_duplicates(subset=['Sequence'])

# label the sequences as high or low based if percentGpA is above or below 0.5
df.loc[df['PercentGpA'] >= 0.5, 'Label'] = 'high'
df.loc[df['PercentGpA'] < 0.5, 'Label'] = 'low'

# define the aas to track
hbond_aas = ['T', 'S']
ring_aas = ['W', 'Y', 'F']

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
    df.loc[df['Sequence'] == seq, 'hbond_ratio'] = 0
    df.loc[df['Sequence'] == seq, 'ring_ratio'] = 0
    if total_count != 0:
        hbond_ratio = hbond_count / total_count 
        ring_ratio = ring_count / total_count
        df.loc[df['Sequence'] == seq, 'hbond_ratio'] = hbond_ratio
        df.loc[df['Sequence'] == seq, 'ring_ratio'] = ring_ratio

        
#altered_df_list.append(df)

# save the dataframe
#names = ['all', 'high', 'low']
#for df, name in zip(altered_df_list, names):
xaxis1 = 'hbond_count'
xaxis2 = 'ring_count'
xaxis3 = 'total_count'
yaxis = 'number_of_sequences'
xaxes = [xaxis1, xaxis2, xaxis3]
# set the x and y axes as integers
df[xaxes] = df[xaxes].astype(int)
for sample in df['Sample'].unique():
    sample_df = df[df['Sample'] == sample]
    sample_df.to_csv(f'{outputDir}/{sample}.csv', index=False)
    sample_dir = f'{outputDir}/{sample}'
    os.makedirs(name=f'{sample_dir}', exist_ok=True)
    for xaxis in xaxes:
        # group the sequences by the number of hbond and ring aas
        grouped_df = sample_df.groupby([xaxis, 'Label']).count().reset_index()
        # set the final column to be the number of sequences (temp; grouped dataframe sets all columns to be the same count, so just use the first column as the count)
        grouped_df.rename(columns={'Sequence': yaxis}, inplace=True)
        print(grouped_df)
        # plot high and low bars next to each other
        barsep = [-0.1, 0.1]
        width = 0.2
        for label,sep in zip(['high', 'low'], barsep):
            label_df = grouped_df[grouped_df['Label'] == label]
            normalized_count = label_df[yaxis] / label_df[yaxis].sum()
            print(normalized_count)
            plt.bar(label_df[xaxis]+sep, normalized_count, label=label, width=width)
        plt.xlabel(xaxis)
        plt.ylabel('Number of Sequences')
        plt.title(f'{sample} {xaxis}')
        plt.legend()
        plt.savefig(f'{sample_dir}/{sample}_{xaxis}.png')
        plt.close()
        # make a pie chart of the hbond and ring ratios
        for label in ['high', 'low']:
            label_df = grouped_df[grouped_df['Label'] == label]
            plt.pie(label_df[yaxis], labels=label_df[xaxis], autopct='%1.1f%%')
            plt.title(f'{sample} {xaxis} {label}')
            # add the total count for each group as a legend
            plt.legend(loc='center left', title='Total Count', labels=label_df[yaxis], bbox_to_anchor=(1, 0.5))
            plt.savefig(f'{sample_dir}/{sample}_{xaxis}_{label}_pie.png')
            plt.close()

#for sample in df['Sample'].unique():
#    sample_df = df[df['Sample'] == sample]
#    sample_df.to_csv(f'{outputDir}/{sample}.csv', index=False)
#    # group the sequences by the number of hbond and ring aas
#    grouped_df = sample_df.groupby([xaxis1, xaxis2, 'Label']).count().reset_index()
#    # plot the data
#    plt.scatter(grouped_df['hbond_count'], grouped_df['ring_count'], s=grouped_df['total_count']*1000, c=grouped_df['total_count'], cmap='viridis')
#    plt.xlabel('Number of Hydrogen Bonding Amino Acids')
#    plt.ylabel('Number of Ring Amino Acids')
#    plt.title(f'{sample} Hydrogen Bonding and Ring Amino Acid Counts')
#    plt.colorbar(label='Number of Sequences')
#    # set the axes to be separated by 1
#    min_ring = grouped_df['ring_count'].min()
#    max_ring = grouped_df['ring_count'].max()
#    plt.xticks(np.arange(0, 4, 1))
#    plt.yticks(np.arange(0, 4, 1))
#    plt.savefig(f'{outputDir}/{sample}.png')
#    plt.close()
df.to_csv(f'{outputDir}/hbond_ring_counts.csv', index=False)
