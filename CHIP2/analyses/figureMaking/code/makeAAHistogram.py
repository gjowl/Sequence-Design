import os, sys, pandas as pd, numpy as np
import matplotlib.pyplot as plt

def getAACounts(input_df, interfaceCol, col):
    df_counts = pd.DataFrame()
    counts, frequencies = [], []
    # get a list of all the potential amino acids
    aas = input_df[interfaceCol].apply(lambda x: pd.Series(list(x))).stack().unique()
    for label in input_df[col].unique():
        df_label = input_df[input_df[col] == label]
        # count the number of each amino acid in the interfaceSeq column
        aa_counts = df_label[interfaceCol].apply(lambda x: pd.Series(list(x))).stack().value_counts()
        # check that all the amino acids are in the counts
        for aa in aas:
            if aa not in aa_counts.index:
                aa_counts[aa] = 0
        # get the total number of amino acids
        total_aa = aa_counts.sum()
        # normalize the counts
        frequency = aa_counts / total_aa
        # append the counts to the counts list
        counts.append(aa_counts)
        frequencies.append(frequency)
    # add the counts to the dataframe
    df_counts['high_count'] = counts[0]
    df_counts['low_count'] = counts[1]
    df_counts['high_frequency'] = frequencies[0]
    df_counts['low_frequency'] = frequencies[1]
    return df_counts

# read in the command line arguments
sequenceFile = sys.argv[1]
outputDir = sys.argv[2]
percentGpaCutoff = float(sys.argv[3])

# make the output directory if it doesn't exist
os.makedirs(name=outputDir, exist_ok=True)

# read in the sequence file reading interface column as a string
df = pd.read_csv(sequenceFile, dtype={'Interface': str})

# keep only non-duplicated sequences
df = df.drop_duplicates(subset=['Sequence'])

#TODO: I think making more ways to break down these (like 3 breakdowns with a difference of 0.25) would be helpful
label_number = 3
# create the labels by the number of labels and the cutoff
cutoff = 0.25
if label_number <= 2:
    df.loc[df['PercentGpA'] >= percentGpaCutoff, 'Label'] = f'>= {percentGpaCutoff}'
    df.loc[df['PercentGpA'] < percentGpaCutoff, 'Label'] = f'< {percentGpaCutoff}'
else:
    for i in range(label_number):
        if i == 0:
            df.loc[df['PercentGpA'] >= percentGpaCutoff, 'Label'] = f'>= {percentGpaCutoff}'
        elif i == label_number - 1:
            final_cutoff = cutoff * (i-1)
            df.loc[df['PercentGpA'] < final_cutoff, 'Label'] = f'< {final_cutoff}'
        else:
            prev_cutoff = percentGpaCutoff - (cutoff * (i+1))
            curr_cutoff = percentGpaCutoff - (cutoff * (i-1))
            print(prev_cutoff, curr_cutoff)
            # get the sequences with a percentGpa between the cutoffs
            df.loc[(df['PercentGpA'] >= prev_cutoff) & (df['PercentGpA'] < curr_cutoff), 'Label'] = f'{prev_cutoff} - {curr_cutoff}'
            #df.loc[df['PercentGpA'] >= percentGpaCutoff, 'Label'] = f'{percentGpaCutoff * i} - {percentGpaCutoff * (i+1)}'
            #df.loc[df['PercentGpA'] < percentGpaCutoff, 'Label'] = f'< {percentGpaCutoff * i}'

# print all of the labels
print(df['Label'].unique())
exit(0)

# remove any labels that are nan
df = df[~df['Label'].isna()]

# define the aas to track
hbond_aas = ['T', 'S']
ring_aas = ['W', 'Y', 'F']

# find positions that are 1 in the interface column for every sequence
interface_positions = df['Interface'].apply(lambda x: [i for i, j in enumerate(x) if j == '1'])

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
    df_counts = getAACounts(df_sample, 'InterfaceSeq', 'Label')
    # make a histogram of the counts
    fig, ax = plt.subplots()
    # sort the counts by index
    high_counts = df_counts['high_frequency'].sort_index()
    low_counts = df_counts['low_frequency'].sort_index()
    # plot the high and low counts adjacent to each other
    ax.bar(np.arange(len(high_counts))-0.2, high_counts, width=0.4, label=f'>= {percentGpaCutoff}', color='forestgreen')
    ax.bar(np.arange(len(low_counts))+0.2, low_counts, width=0.4, label=f'< {percentGpaCutoff}', color='lightsteelblue')
    ax.set_xticks(np.arange(len(high_counts)))
    ax.set_xticklabels(high_counts.index)
    ax.set_title(f'{sample}')
    # set the legend
    ax.legend()
    # set the y limit
    ax.set_ylim(0, 0.35)
    ax.set_xlabel('Amino Acid')
    ax.set_ylabel('Frequency')
    # add the total number of sequences and the number of sequences in each group as a text box
    ax.text(0.05, 1.15, f'Total Sequences: {len(df_sample)}', transform=ax.transAxes, fontsize=10, verticalalignment='top')
    ax.text(0.05, 1.1, f'>= {percentGpaCutoff}: {len(df_sample[df_sample["Label"] == "high"])}', transform=ax.transAxes, fontsize=10, verticalalignment='top')
    ax.text(0.05, 1.05, f'< {percentGpaCutoff}: {len(df_sample[df_sample["Label"] == "low"])}', transform=ax.transAxes, fontsize=10, verticalalignment='top') 
    plt.savefig(f'{outputDir}/{sample}.png')
    plt.close()
    # save the counts to a csv
    df_counts.to_csv(f'{outputDir}/{sample}.csv')
    # save the dataframe to a csv
    df_sample.to_csv(f'{outputDir}/{sample}_df.csv')
