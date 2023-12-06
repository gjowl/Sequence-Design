import os, sys, pandas as pd, numpy as np
import matplotlib.pyplot as plt

def getAACounts(input_df, interfaceCol, col):
    counts = []
    for label in input_df[col].unique():
        df_label = df_sample[df_sample[col] == label]
        # count the number of each amino acid in the interfaceSeq column
        aa_counts = df_label[interfaceCol].apply(lambda x: pd.Series(list(x))).stack().value_counts()
        # get the total number of amino acids
        total_aa = aa_counts.sum()
        # normalize the counts
        aa_counts = aa_counts / total_aa
        # append the counts to the counts list
        counts.append(aa_counts)
    return counts[0], counts[1]

# read in the command line arguments
sequenceFile = sys.argv[1]
outputDir = sys.argv[2]

# make the output directory if it doesn't exist
os.makedirs(name=outputDir, exist_ok=True)

# read in the sequence file reading interface column as a string
df = pd.read_csv(sequenceFile, dtype={'Interface': str})

# keep only non-duplicated sequences
df = df.drop_duplicates(subset=['Sequence'])

# label the sequences as high or low based if percentGpA is above or below 0.5
df.loc[df['PercentGpA'] >= 0.5, 'Label'] = 'high'
df.loc[df['PercentGpA'] < 0.5, 'Label'] = 'low'

# remove any labels that are nan
df = df[~df['Label'].isna()]

# define the aas to track
hbond_aas = ['T', 'S']
ring_aas = ['W', 'Y', 'F']

print(df)
# find positions that are 1 in the interface column for every sequence
interface_positions = df['Interface'].apply(lambda x: [i for i, j in enumerate(x) if j == '1'])
print(interface_positions)

# get the positions at the interface positions in each sequence
interface_seqs = []
for sequence, interface in zip(df['Sequence'], interface_positions):
    interface_seq = ''
    for pos in interface:
            interface_seq += sequence[pos]
    interface_seqs.append(interface_seq)

df['InterfaceSeq'] = interface_seqs

# loop through the samples and make a histogram for each
for sample in df['Sample'].unique():
    df_sample = df[df['Sample'] == sample]
    high_counts, low_counts = getAACounts(df_sample, 'InterfaceSeq', 'Label')
    # make a histogram of the counts
    fig, ax = plt.subplots()
    # plot the high and low counts adjacent to each other
    ax.bar(np.arange(len(high_counts))-0.2, high_counts, width=0.4, label='High', color='green')
    ax.bar(np.arange(len(low_counts))+0.2, low_counts, width=0.4, label='Low')
    ax.set_xticks(np.arange(len(high_counts)))
    ax.set_xticklabels(high_counts.index)
    ax.set_title(f'{sample}')
    # set the legend
    ax.legend()
    #ax.set_title(f'{sample}')
    # set the y limit
    ax.set_ylim(0, 0.3)
    ax.set_xlabel('Amino Acid')
    ax.set_ylabel('Count')
    plt.savefig(f'{outputDir}/{sample}.png')
    plt.close()
    print(sample)
