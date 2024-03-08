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
        df_counts[f'{label}_freq'] = frequency
        df_counts[f'{label}_count'] = aa_counts
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
label_number = 5
# create the labels by the number of labels and the cutoff
cutoff = 0.25
if label_number <= 2:
    df.loc[df['PercentGpA'] >= percentGpaCutoff, 'Label'] = f'>= {percentGpaCutoff}'
    df.loc[df['PercentGpA'] < percentGpaCutoff, 'Label'] = f'< {percentGpaCutoff}'
else:
    for i in range(label_number):
        if i == 0:
            df.loc[df['PercentGpA'] >= percentGpaCutoff, 'Label'] = f'>= {percentGpaCutoff}'
            prev_cutoff = percentGpaCutoff
        elif i == label_number - 1:
            final_cutoff = prev_cutoff * i
            df.loc[df['PercentGpA'] < final_cutoff, 'Label'] = f'< {final_cutoff}'
        else:
            low_cutoff = percentGpaCutoff - (cutoff * i)
            print(low_cutoff, prev_cutoff)
            # get the sequences with a percentGpa between the cutoffs
            df.loc[(df['PercentGpA'] >= low_cutoff) & (df['PercentGpA'] < prev_cutoff), 'Label'] = f'{low_cutoff} - {prev_cutoff}'
            prev_cutoff = low_cutoff

# print all of the labels
print(df['Label'].unique())

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
plot_by = 'freq'
# loop through the samples and make a histogram for each
for sample in df['Sample'].unique():
    df_sample = df[df['Sample'] == sample]
    df_counts = getAACounts(df_sample, 'InterfaceSeq', 'Label')
    # make a histogram of the counts
    fig, ax = plt.subplots()
    for label, i in zip(df_counts.columns, range(len(df_counts.columns))):
        # keep only the columns that match the plot_by
        df_plot = df_counts[[col for col in df_counts.columns if plot_by in col]]
        [print(df_plot)]
        if plot_by in label:
            sorted_counts = df_plot[label].sort_index()
            # check if i is half of the number of columns (rounded up)
            if i == np.ceil(len(df_plot.columns) / 2):
                ax.bar(np.arange(len(sorted_counts)), sorted_counts, width=0.1, label=label)
                print(i)
            elif i > np.ceil(len(df_plot.columns) / 2):
                ax.bar(np.arange(len(sorted_counts))+(0.05 * i), sorted_counts, width=0.1, label=label)
            elif i < np.ceil(len(df_plot.columns) / 2):
                ax.bar(np.arange(len(sorted_counts))-(0.05 * i), sorted_counts, width=0.1, label=label)
    ax.set_ylim(0, 0.35)
    ax.set_ylabel('Frequency')
    ax.set_xlabel('Amino Acid')
    ax.set_xticks(np.arange(len(sorted_counts)))
    ax.set_xticklabels(sorted_counts.index)
    ax.set_title(f'{sample}')
    # set the legend
    ax.legend()
    # add the total number of sequences and the number of sequences in each group as a text box
    #ax.text(0.05, 1.15, f'Total Sequences: {len(df_sample)}', transform=ax.transAxes, fontsize=10, verticalalignment='top')
    #ax.text(0.05, 1.1, f'>= {percentGpaCutoff}: {len(df_sample[df_sample["Label"] == "high"])}', transform=ax.transAxes, fontsize=10, verticalalignment='top')
    #ax.text(0.05, 1.05, f'< {percentGpaCutoff}: {len(df_sample[df_sample["Label"] == "low"])}', transform=ax.transAxes, fontsize=10, verticalalignment='top') 
    plt.savefig(f'{outputDir}/{sample}.png')
    plt.close()
    # save the counts to a csv
    df_counts.to_csv(f'{outputDir}/{sample}.csv')
    # save the dataframe to a csv
    df_sample.to_csv(f'{outputDir}/{sample}_df.csv')
