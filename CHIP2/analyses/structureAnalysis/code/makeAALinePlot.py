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

def addLabels(input_df, number_of_labels, cutoff, percentGpaCutoff):
    output_df = input_df.copy()
    if number_of_labels <= 2:
        output_df.loc[output_df['PercentGpA'] >= percentGpaCutoff, 'Label'] = f'>= {percentGpaCutoff}'
        output_df.loc[output_df['PercentGpA'] < percentGpaCutoff, 'Label'] = f'< {percentGpaCutoff}'
    else:
        for i in range(number_of_labels):
            if i == 0:
                output_df.loc[output_df['PercentGpA'] >= percentGpaCutoff, 'Label'] = f'>= {percentGpaCutoff}'
                prev_cutoff = percentGpaCutoff
            elif i == number_of_labels - 1:
                final_cutoff = round(prev_cutoff * i, 2)
                output_df.loc[output_df['PercentGpA'] < final_cutoff, 'Label'] = f'< {final_cutoff}'
            else:
                low_cutoff = round(percentGpaCutoff - (cutoff * i), 2)
                # get the sequences with a percentGpa between the cutoffs
                output_df.loc[(output_df['PercentGpA'] >= low_cutoff) & (output_df['PercentGpA'] < prev_cutoff), 'Label'] = f'{low_cutoff} - {prev_cutoff}'
                prev_cutoff = low_cutoff
    return output_df

# read in the command line arguments
sequenceFile = sys.argv[1]
outputDir = sys.argv[2]
percentGpaCutoff = float(sys.argv[3])
number_of_labels = int(sys.argv[4])
cutoff = float(sys.argv[5])

# make the output directory if it doesn't exist
os.makedirs(name=outputDir, exist_ok=True)

# read in the sequence file reading interface column as a string
df = pd.read_csv(sequenceFile, dtype={'Interface': str})

# keep only non-duplicated sequences
df = df.drop_duplicates(subset=['Sequence'])

# create the labels by the number of labels and the cutoff
df = addLabels(df, number_of_labels, cutoff, percentGpaCutoff)

# remove any labels that are nan
df = df[~df['Label'].isna()]

# only keep the labels in the Label column
labels = df['Label'].unique()

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
    text_y = 1.15
    divider = 0.03
    # keep the columns that match the plot_by
    df_plot = df_counts[[col for col in df_counts.columns if plot_by in col]]
    # remove the plot_by from the column names
    df_plot.columns = [col.split('_')[0] for col in df_plot.columns]
    for label, i in zip(labels, range(len(labels))):
        sorted_counts = df_plot[label].sort_index()
        ax.plot(np.arange(len(sorted_counts)), sorted_counts, linestyle='--', label=label)
        # write the count on the plot
        # get the label without the plot_by
        label = label.split('_')[0]
        if i == 0:
            ax.text(0.05, 1.15, f'{label}: {len(df_sample[df_sample["Label"] == label])}', transform=ax.transAxes, fontsize=10, verticalalignment='top')
        else:
            curr_text_y = text_y - (divider * i)
            ax.text(0.05, curr_text_y, f'{label}: {len(df_sample[df_sample["Label"] == label])}', transform=ax.transAxes, fontsize=10, verticalalignment='top')
    ax.set_ylim(0, 0.35)
    ax.set_ylabel('Frequency')
    ax.set_xlabel('Amino Acid')
    ax.set_xticks(np.arange(len(sorted_counts)))
    ax.set_xticklabels(sorted_counts.index)
    ax.set_title(f'{sample}')
    # set the legend
    ax.legend()
    plt.savefig(f'{outputDir}/{sample}.png')
    plt.clf()
    # save the counts to a csv
    df_counts.to_csv(f'{outputDir}/{sample}.csv')
    # save the dataframe to a csv
    df_sample.to_csv(f'{outputDir}/{sample}_df.csv')
