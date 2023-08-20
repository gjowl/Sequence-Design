
import sys, os, pandas as pd, numpy as np, matplotlib.pyplot as plt

def match(s1, s2):
    num_diff = 0
    for i, (c1, c2) in enumerate(zip(s1, s2)):
        if c1 != c2:
            num_diff += 1
    return num_diff 

def getMismatchedPosition(s1, s2):
    for i, (c1, c2) in enumerate(zip(s1, s2)):
        if c1 != c2:
            return i, c1, c2
    return -1, -1, -1
#def calculatePercentDifference(df_match, seq_fluor): 
#    output_df = df_match.copy()
#    # calculate the percent difference between the sequence and the mutant
#    output_df['percent_difference'] = output_df[fluor_col].apply(lambda x: (x - seq_fluor) / seq_fluor * 100)
#    return output_df

def calculatePercentWt(df_match, seq_fluor): 
    output_df = df_match.copy()
    # calculate the percent difference between the sequence and the mutant
    output_df['percent_wt'] = output_df[fluor_col].apply(lambda x: x / seq_fluor * 100)
    # if percent_wt is NA, set it to 0
    output_df['percent_wt'] = output_df['percent_wt'].fillna(0)
    return output_df

def plotBarGraph(df_seq, xaxis, yaxis, xaxis_labels, seq, output_dir):  
    ax = plt.subplot(111)
    increment = 0.2
    plt.bar(df_seq[xaxis], df_seq[yaxis], width=0.4, color='g')
    # set the x ticks to be the sequence names
    ax.set_xticklabels(xaxis_labels)
    # rotate the x ticks
    #plt.xticks(rotation=90)
    plt.xlabel(xaxis)
    plt.ylabel(yaxis)
    plt.title('Average fluorescence of design sequences separated by sample')
    # set the legend
    #ax.legend()
    ax.autoscale(tight=False)
    plt.savefig(f'{output_dir}/{seq}.png')
    plt.clf()

def addMismatchedPositions(df, wt_seq_col, position_col):
    input_df = df.copy()
    output_df = pd.DataFrame()
    for sample in samples:
        df_sample = input_df[input_df['Sample'] == sample]
        for seq in input_df[wt_seq_col].unique():
            # get only a set of sequences that differ by the nonmatching_aa_min
            df_seq = df_sample[df_sample[wt_seq_col] == seq].copy()
            aa_pos_list = []
            for seq2 in df_seq['Sequence'].unique():
                position, aa1, aa2 = getMismatchedPosition(seq, seq2)
                aa_pos = f'{aa1}{position}{aa2}'
                aa_pos_list.append(aa_pos)
            df_seq[position_col] = aa_pos_list
            output_df = pd.concat([output_df, df_seq])
    return output_df

# read in the input files
fluorFile = sys.argv[1]
output_dir = sys.argv[2]

os.makedirs(output_dir, exist_ok=True)
#sequenceFile = sys.argv[1]
#mutantFile = sys.argv[2]

# read in the dataframes
df_fluor = pd.read_csv(fluorFile)
fluor_col = 'mean_transformed'
percent_cutoff = 75
nonmatching_aa_min = 2
matching_seq_min = 3
wt_seq_col = 'wt_seq'
position_col = 'position'
#df_sequence = pd.read_csv(sequenceFile)
#df_mutant = pd.read_csv(mutantFile)

samples = df_fluor['Sample'].unique()
output_lowPerc = pd.DataFrame()
output_highPerc = pd.DataFrame()
output_other = pd.DataFrame()
for sample in samples:
    numSeqs = 0
    highSeqs = 0
    usableSeqs = 0
    df_sample = df_fluor[df_fluor['Sample'] == sample]
    # loop through all of the sequences
    for seq in df_sample[df_sample['Type'] == 'WT']['Sequence'].unique():
        if df_sample[df_sample['Sequence'] == seq][fluor_col].values[0] == 0:
            continue
        matching_sequences = [seq]
        for seq2 in df_sample['Sequence'].unique():
            if match(seq, seq2) < nonmatching_aa_min:
                matching_sequences.append(seq2)
        # keep only the unique sequences
        matching_sequences = list(set(matching_sequences))
        if len(matching_sequences) > matching_seq_min:
            numSeqs += 1
        else:
            continue
        df_match = df_sample[df_sample['Sequence'].isin(matching_sequences)]
        # get the sequence with the highest fluorescence
        seq_fluor = df_match[df_match['Sequence'] == seq][fluor_col].values[0]
        df_percDiff = calculatePercentWt(df_match, seq_fluor)
        df_percDiff[wt_seq_col] = seq
        df_otherSeqs = df_percDiff[df_percDiff['Sequence'] != seq]
        # check if all percent wt are greater than the percent difference cutoff
        if df_otherSeqs['percent_wt'].max() < percent_cutoff:
            usableSeqs += 1
            output_lowPerc = pd.concat([output_lowPerc, df_percDiff])
        elif df_otherSeqs['percent_wt'].min() > percent_cutoff:
            highSeqs += 1
            output_highPerc = pd.concat([output_highPerc, df_percDiff])
        else:
            output_other = pd.concat([output_other, df_percDiff])
        # think of a way to keep the mutants that also don't fluoresce here? Maybe if I just label each sequence as a mutant or not?
        # also could output a dataframe of seqs that aren't present in mutant or sequence file? or just not in refseqs?
        # also, should I keep the maltose cutoff too? that way, if something with like a G83i like mutation is gone, that can be the justification?
        #exit(0)
    print(sample, numSeqs, usableSeqs, highSeqs)



output_df = pd.concat([output_lowPerc, output_highPerc, output_other])
# add mismatched position to dataframe
output_df = addMismatchedPositions(output_df, wt_seq_col, position_col)
output_df['wt_aa'] = output_df[position_col].apply(lambda x: x[0])
output_df['mut_aa'] = output_df[position_col].apply(lambda x: x[-1])
output_df['position'] = output_df[position_col].apply(lambda x: x[1:-1])
output_df = output_df[output_df['percent_wt'] < 200]
output_lowPerc = output_df[output_df['percent_wt'] < percent_cutoff]
output_highPerc = output_df[output_df['percent_wt'] > 125]
output_other = output_df[(output_df['percent_wt'] >= percent_cutoff) & (output_df['percent_wt'] <= 125)]
output_df = output_df[output_df[position_col] != '-1-1-1']
output_lowPerc.to_csv(f'{output_dir}/below_{percent_cutoff}.csv', index=False)
output_highPerc.to_csv(f'{output_dir}/above_{percent_cutoff}.csv', index=False)
output_other.to_csv(f'{output_dir}/other.csv', index=False)
output_zero = output_df[output_df['percent_wt'] == 0]
dfs = [output_lowPerc, output_highPerc, output_other]
output_names = ['less75', 'more125', 'wt_like']
for df,name in zip(dfs, output_names): 
    for sample in samples:
        df_sample = df[df['Sample'] == sample]
        count = 0
        graph_count = 0
        sample_dir = f'{output_dir}/{sample}/{name}'
        os.makedirs(sample_dir, exist_ok=True)
        for pos in df_sample[position_col].unique():
            if pos != '-1-1-1':
                df_pos = df_sample[df_sample[position_col] == pos]
                x = df_pos['percent_wt']
                # maybe this works? Still too many around 0, maybe find a way to get rid of anything without a certain y value?
                # also run this on the sequences that don't fluoresce as well and compare to see if there are any things that are significantly different
                # get highest percent wt
                high = df_pos['percent_wt'].max()
                if len(x) < 10:
                    continue
                #elif count < 4:
                #    plt.hist(x, bins=len(x), alpha=0.5, label=pos, edgecolor='black', linewidth=1.2)
                #    count += 1
                else:
                    #count = 0
                    #graph_count += 1
                    plt.hist(x, bins=5, alpha=0.5, label=pos, edgecolor='black', linewidth=1.2)
                    plt.xlabel('Percent WT')
                    plt.ylabel('Frequency') 
                    plt.legend(loc='upper right')
                    plt.tight_layout()
                    plt.savefig(f'{sample_dir}/{pos}.png')
                    plt.clf()
    #plt.legend(loc='upper right')
    #plt.tight_layout()
    #plt.savefig(f'{output_dir}/{sample}_{pos}.png')
    #plt.clf()
clash_df = output_df[output_df['Mutant Type'] == 'clash']
void_df = output_df[output_df['Mutant Type'] == 'void']
wt_clash = output_df[output_df['Sequence'].isin(clash_df['wt_seq'])]
wt_clash = wt_clash.drop_duplicates(subset=['Sequence'])
clash_df = pd.concat([clash_df, wt_clash])
wt_void = output_df[output_df['Sequence'].isin(void_df['wt_seq'])]
wt_void = wt_void.drop_duplicates(subset=['Sequence'])
void_df = pd.concat([void_df, wt_void])
clash_df.to_csv(f'{output_dir}/clash.csv', index=False)
void_df.to_csv(f'{output_dir}/void.csv', index=False)
gtoi_df = output_df[output_df['wt_aa'] == 'G']
gtoi_df = gtoi_df[gtoi_df['mut_aa'] == 'I']
gtoi_df = gtoi_df[gtoi_df['percent_wt'] < 75]
# append the wt sequence to the dataframe
wt_gtoi = output_df[output_df['Sequence'].isin(gtoi_df['wt_seq'])]
wt_gtoi = wt_gtoi.drop_duplicates(subset=['Sequence'])
gtoi_df = pd.concat([gtoi_df, wt_gtoi])
gtoi_df.to_csv(f'{output_dir}/g_to_i_mutants.csv', index=False)
# get the wt and mutant aas and positions in separate columns
# maybe analyze sequences that have percent wt < 100?
## plot bar graph
#xaxis = 'position'
#xaxis_labels = df_seq[xaxis]
## replace the first label with seq
#xaxis_labels.iloc[0] = seq
#yaxis = 'percent_wt'
#plotBarGraph(df_seq, xaxis, yaxis, xaxis_labels, seq, output_dir)
    
# Currently works for individual sequences; next, run on all similar positions, naming them by something else? Or could I do like a multi bar graph plot, with
# multiple positions at the labels and minibar graphs for each? Like a histogram of each; can also do frequency of each in the sequences that succeed and that fail
# https://stackoverflow.com/questions/6871201/plot-two-histograms-on-single-chart-with-matplotlib
# https://stackoverflow.com/questions/47467077/python-plot-multiple-histograms
# int(df_seq)
exit(0)
            