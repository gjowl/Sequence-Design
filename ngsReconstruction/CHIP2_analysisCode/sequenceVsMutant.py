
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
    #ax.set_xticklabels(xaxis_labels)
    # rotate the x ticks
    plt.xticks(rotation=45)
    plt.xlabel(xaxis)
    plt.ylabel(yaxis)
    plt.title('Percent WT per Mutant')
    # set the legend
    #ax.legend()
    # bold the first and last letter in the each xaxis label
    for label in ax.get_xticklabels():
        label.set_fontweight('bold')
    # add the number with first two decimals to the top of each bar
    for i, v in enumerate(df_seq[yaxis]):
        ax.text(i-increment, v+0.25, f'{v:.2f}%', color='black', fontweight='bold')
    ax.autoscale(tight=False)
    plt.tight_layout()
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

def mutantTrimmingFunction(wt_df, mutant_df, trimming_col, seq_col, percent_cutoff, fraction_sequence_cutoff):
    output_df = wt_df.copy()
    input_df = mutant_df.copy()
    input_df = input_df.groupby(seq_col).filter(lambda x: len(x[x[trimming_col] < percent_cutoff]) > fraction_sequence_cutoff*len(x))
    output_df = output_df[output_df[seq_col].isin(input_df[seq_col])]
    return output_df

def getSimilarSequences(df, seq, nonmatching_aa_min):
    input_df = df.copy()
    output_df = pd.DataFrame()
    samples = input_df['Sample'].unique()
    for sample in samples:
        df_sample = input_df[input_df['Sample'] == sample]
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
            if len(matching_sequences) < matching_seq_min:
                continue
            df_match = df_sample[df_sample['Sequence'].isin(matching_sequences)]
            # get the sequence with the highest fluorescence
            seq_fluor = df_match[df_match['Sequence'] == seq][fluor_col].values[0]
            df_percDiff = calculatePercentWt(df_match, seq_fluor)
            df_percDiff[wt_seq_col] = seq
            df_otherSeqs = df_percDiff[df_percDiff['Sequence'] != seq]
            output_df = pd.concat([output_df, df_percDiff])
            # check if all percent wt are greater than the percent difference cutoff
            #if df_otherSeqs['percent_wt'].max() < percent_cutoff:
            #    usableSeqs += 1
            #    output_lowPerc = pd.concat([output_lowPerc, df_percDiff])
            #elif df_otherSeqs['percent_wt'].min() > percent_cutoff:
            #    highSeqs += 1
            #    output_highPerc = pd.concat([output_highPerc, df_percDiff])
            #else:
            #    output_other = pd.concat([output_other, df_percDiff])
        #print(sample, numSeqs, usableSeqs, highSeqs)
    return output_df

# read in the input files
fluorFile = sys.argv[1]
outputDir = sys.argv[2]

os.makedirs(outputDir, exist_ok=True)
#sequenceFile = sys.argv[1]
#mutantFile = sys.argv[2]

# read in the dataframes
df_fluor = pd.read_csv(fluorFile)
fluor_col = 'mean_transformed'
percent_cutoff = 75
high_cutoff = 125
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

output_df = getSimilarSequences(df_fluor, wt_seq_col, nonmatching_aa_min)
output_df.to_csv(f'{outputDir}/all.csv', index=False)
output_df_2 = getSimilarSequences(df_fluor, wt_seq_col, 3)
output_df_2.to_csv(f'{outputDir}/all_seqDiff_2.csv', index=False)
output_df_3 = getSimilarSequences(df_fluor, wt_seq_col, 4)
output_df_3.to_csv(f'{outputDir}/all_seqDiff_3.csv', index=False)
output_df_4 = getSimilarSequences(df_fluor, wt_seq_col, 5)
output_df_4.to_csv(f'{outputDir}/all_seqDiff_4.csv', index=False)
output_df_5 = getSimilarSequences(df_fluor, wt_seq_col, 6)
output_df_5.to_csv(f'{outputDir}/all_seqDiff_5.csv', index=False)

# add mismatched position to dataframe
output_df = addMismatchedPositions(output_df, wt_seq_col, position_col)
output_df['wt_aa'] = output_df[position_col].apply(lambda x: x[0])
output_df['mut_aa'] = output_df[position_col].apply(lambda x: x[-1])
output_df['mut_position'] = output_df[position_col].apply(lambda x: x[1:-1])
output_df = output_df[output_df['percent_wt'] < 200]
output_df.to_csv(f'{outputDir}/less_than_200_percentWT.csv', index=False)
output_df = output_df[output_df['Percent GpA'] < 150]
output_df.to_csv(f'{outputDir}/less_than_150_percentGpA.csv', index=False)
#output_df = output_df[output_df['Percent Error'] < 10]
maltose_col = 'LB-12H_M9-36H'
maltose_cutoff = -100
maltose_limit = 99999900 
wt_cutoff = 110
output_df = output_df[output_df[maltose_col] < maltose_limit]
output_df = output_df[output_df[maltose_col] > maltose_cutoff]
output_df.to_csv(f'{outputDir}/maltose_passing.csv', index=False)
output_lowPerc = output_df[output_df['percent_wt'] < percent_cutoff]
output_highPerc = output_df[output_df['percent_wt'] > high_cutoff]
output_other = output_df[(output_df['percent_wt'] >= percent_cutoff) & (output_df['percent_wt'] <= high_cutoff)]
output_other.to_csv(f'{outputDir}/between_{percent_cutoff}_and_{high_cutoff}_percentWT.csv', index=False)
#output_df = output_df[output_df[position_col] != '-1-1-1']
output_lowPerc.to_csv(f'{outputDir}/below_{percent_cutoff}.csv', index=False)
output_highPerc.to_csv(f'{outputDir}/above_{high_cutoff}.csv', index=False)
output_wtLike = output_df[output_df['percent_wt'] <= wt_cutoff]
# check that the type is not WT
output_df_mut = output_df[output_df['Type'] != 'WT']
output_df_wt = output_df[output_df['Type'] == 'WT']
output_df_mut_less = output_df_mut[output_df_mut['percent_wt'] < wt_cutoff].copy()
output_df_wtlike = output_df_wt[output_df_wt['wt_seq'].isin(output_df_mut_less['wt_seq'])]
#output_df_wtlike.to_csv(f'{outputDir}/wt_like_any_mutants_lessThan_{percent_cutoff}.csv', index=False)
# check to see if 80% of the sequences per each wt_seq are less than 75% wt
trim_col = 'percent_wt'
seq_col = 'wt_seq'
output_wtLike_all = mutantTrimmingFunction(output_df_wt, output_df_mut, trim_col, seq_col, percent_cutoff, 1)
output_wtLike_75 = mutantTrimmingFunction(output_df_wt, output_df_mut, trim_col, seq_col, percent_cutoff, 0.75)
output_wtLike_50 = mutantTrimmingFunction(output_df_wt, output_df_mut, trim_col, seq_col, percent_cutoff, 0.5)
output_wtLike_25 = mutantTrimmingFunction(output_df_wt, output_df_mut, trim_col, seq_col, percent_cutoff, 0.25)
output_wtLike_any = mutantTrimmingFunction(output_df_wt, output_df_mut, trim_col, seq_col, percent_cutoff, 0)
output_wtLike_all.to_csv(f'{outputDir}/all_mutants_lessThan_{percent_cutoff}.csv', index=False)
output_wtLike_75.to_csv(f'{outputDir}/75_percent_mutants_lessThan_{percent_cutoff}.csv', index=False)
output_wtLike_50.to_csv(f'{outputDir}/50_percent_mutants_lessThan_{percent_cutoff}.csv', index=False)
output_wtLike_25.to_csv(f'{outputDir}/25_percent_mutants_lessThan_{percent_cutoff}.csv', index=False)
output_wtLike_any.to_csv(f'{outputDir}/any_mutants_lessThan_{percent_cutoff}.csv', index=False)
output_wtLike.to_csv(f'{outputDir}/percentWT_lessThan_{wt_cutoff}.csv', index=False)

output_zero = output_df[output_df['percent_wt'] == 0]
dfs = [output_lowPerc, output_highPerc, output_other]
output_names = ['less75', 'more125', 'wt_like']
for df,name in zip(dfs, output_names): 
    for sample in samples:
        df_sample = df[df['Sample'] == sample]
        count = 0
        graph_count = 0
        sample_dir = f'{outputDir}/{sample}/{name}'
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
    #plt.savefig(f'{outputDir}/{sample}_{pos}.png')
    #plt.clf()
clash_df = output_df[output_df['Mutant Type'] == 'clash']
void_df = output_df[output_df['Mutant Type'] == 'void']
wt_clash = output_df[output_df['Sequence'].isin(clash_df['wt_seq'])]
wt_clash = wt_clash.drop_duplicates(subset=['Sequence'])
clash_df = pd.concat([clash_df, wt_clash])
wt_void = output_df[output_df['Sequence'].isin(void_df['wt_seq'])]
wt_void = wt_void.drop_duplicates(subset=['Sequence'])
void_df = pd.concat([void_df, wt_void])
clash_df.to_csv(f'{outputDir}/clash.csv', index=False)
void_df.to_csv(f'{outputDir}/void.csv', index=False)
gtoi_df = output_df[output_df['wt_aa'] == 'G']
gtoi_df = gtoi_df[gtoi_df['mut_aa'] == 'I']
gtoi_df = gtoi_df[gtoi_df['percent_wt'] < percent_cutoff]
# append the wt sequence to the dataframe
wt_gtoi = output_df[output_df['Sequence'].isin(gtoi_df['wt_seq'])]
wt_gtoi = wt_gtoi.drop_duplicates(subset=['Sequence'])
gtoi_df = pd.concat([gtoi_df, wt_gtoi])
gtoi_df.to_csv(f'{outputDir}/g_to_i_mutants.csv', index=False)
clash_df_wt = clash_df[clash_df['percent_wt'] < wt_cutoff]
clash_df_less = clash_df[clash_df['percent_wt'] < percent_cutoff]
clash_df_wt.to_csv(f'{outputDir}/clash_wt.csv', index=False)
clash_df_less.to_csv(f'{outputDir}/clash_less.csv', index=False)
void_df_wt = void_df[void_df['percent_wt'] < wt_cutoff]
void_df_less = void_df[void_df['percent_wt'] < percent_cutoff]
void_df_wt.to_csv(f'{outputDir}/void_wt.csv', index=False)
void_df_less.to_csv(f'{outputDir}/void_less.csv', index=False)

# mut_aa A mutants
#def getSpecificMutants(df, mut_aa):
#    output_df = df[df['mut_aa'] == mut_aa]
#    return output_df
a_df = output_df[output_df['mut_aa'] == 'A']
a_df_less = a_df[a_df['percent_wt'] < percent_cutoff]
a_df_more = a_df[a_df['percent_wt'] > high_cutoff]
a_df_less.to_csv(f'{outputDir}/a_less.csv', index=False)
a_df_more.to_csv(f'{outputDir}/a_more.csv', index=False)
a_df_wt = a_df[a_df['percent_wt'] < wt_cutoff]
a_df_wt.to_csv(f'{outputDir}/a_wt.csv', index=False)
gtoi_a_df = gtoi_df[gtoi_df['wt_seq'].isin(a_df_less['wt_seq'])]
gtoi_a_df.to_csv(f'{outputDir}/g_to_i_AND_x_to_a.csv', index=False)
f_df = output_df[output_df['mut_aa'] == 'F']
f_df_less = f_df[f_df['percent_wt'] < percent_cutoff]
f_df_more = f_df[f_df['percent_wt'] > high_cutoff]
f_df_less.to_csv(f'{outputDir}/f_less.csv', index=False)
f_df_more.to_csv(f'{outputDir}/f_more.csv', index=False)
f_df_wt = f_df[f_df['percent_wt'] < wt_cutoff]
f_df_wt.to_csv(f'{outputDir}/f_wt.csv', index=False)
gtoi_f_df = gtoi_df[gtoi_df['wt_seq'].isin(f_df_less['wt_seq'])]
gtoi_f_df.to_csv(f'{outputDir}/g_to_i_AND_x_to_f.csv', index=False)
y_df = output_df[output_df['mut_aa'] == 'Y']
y_df_less = y_df[y_df['percent_wt'] < percent_cutoff]
y_df_more = y_df[y_df['percent_wt'] > high_cutoff]
y_df_less.to_csv(f'{outputDir}/y_less.csv', index=False)
y_df_more.to_csv(f'{outputDir}/y_more.csv', index=False)
y_df_wt = y_df[y_df['percent_wt'] < wt_cutoff]
y_df_wt.to_csv(f'{outputDir}/y_wt.csv', index=False)
gtoi_y_df = gtoi_df[gtoi_df['wt_seq'].isin(y_df_less['wt_seq'])]
gtoi_y_df.to_csv(f'{outputDir}/g_to_i_AND_x_to_y.csv', index=False)


# get sequences that have a successful g83i mutation
gtoi_df_allWts = output_df[output_df['wt_seq'].isin(gtoi_df['wt_seq'])]
gtoi_df_allWts.to_csv(f'{outputDir}/g_to_i_test.csv', index=False)

for seq in gtoi_df_allWts['wt_seq'].unique():
    df_seq = gtoi_df_allWts[gtoi_df_allWts['wt_seq'] == seq]
    #df_seq = df_seq[df_seq['percent_wt'] < 75]
    #df_seq = df_seq[df_seq['percent_wt'] > 0]
    #df_seq = df_seq[df_seq['position'] != '-1-1-1']
    #df_seq = df_seq.drop_duplicates(subset=['position'])
    #df_seq = df_seq.sort_values(by=['position'])
    # sort df by percent wt after the percent wt that is 100
    df_seq = df_seq.sort_values(by=['percent_wt'], ascending=False)
    # move the percent wt that is 100 to the top
    df_seq = pd.concat([df_seq[df_seq['percent_wt'] == 100], df_seq[df_seq['percent_wt'] != 100]])
    #df_seq['position'] = df_seq['position'].apply(lambda x: int(x))
    # get the wt and mutant aas and positions in separate columns
    # maybe analyze sequences that have percent wt < 100?
    # plot bar graph
    xaxis = 'position'
    xaxis_labels = df_seq[xaxis].copy()
    # replace position '-1-1-1' with seq
    df_seq['position'] = df_seq['position'].replace('-1-1-1', seq)
    # replace the first label with seq
    xaxis_labels.iloc[0] = seq
    yaxis = 'percent_wt'
    outDir = f'{outputDir}/g_to_i_mutants'
    os.makedirs(outDir, exist_ok=True)
    plotBarGraph(df_seq, xaxis, yaxis, xaxis_labels, seq, outDir) 
# get the wt and mutant aas and positions in separate columns
# maybe analyze sequences that have percent wt < 100?
## plot bar graph
#xaxis = 'position'
#xaxis_labels = df_seq[xaxis]
## replace the first label with seq
#xaxis_labels.iloc[0] = seq
#yaxis = 'percent_wt'
#plotBarGraph(df_seq, xaxis, yaxis, xaxis_labels, seq, outputDir)

# TODO: take the all data dataframe, read it, and plot the energy score for each sequence that is WT and 1 amino acid off, then 2, then 3, etc.
# look at sequences that are mutants of a single sequence
#for wt_seq in output_df['wt_seq'].unique():
#    df_seq = output_df[output_df['wt_seq'] == wt_seq]
#    df_seq = df_seq[df_seq['Type'] == 'WT']
#    df_seq.to_csv(f'{outputDir}/{wt_seq}.csv', index=False)
## TODO: look at individual mutations of each sequence
## Plot bar graphs of any sequences that have a successful g83i mutation? That way I can see all of the mutants 
## Currently works for individual sequences; next, run on all similar positions, naming them by something else? Or could I do like a multi bar graph plot, with
## multiple positions at the labels and minibar graphs for each? Like a histogram of each; can also do frequency of each in the sequences that succeed and that fail
## https://stackoverflow.com/questions/6871201/plot-two-histograms-on-single-chart-with-matplotlib
## https://stackoverflow.com/questions/47467077/python-plot-multiple-histograms
## int(df_seq)
#exit(0)
#            