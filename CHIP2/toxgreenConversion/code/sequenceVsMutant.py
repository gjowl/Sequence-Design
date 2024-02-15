
import sys, os, pandas as pd, numpy as np, matplotlib.pyplot as plt, argparse

# initialize the parser
parser = argparse.ArgumentParser(description='Compare the fluorescence of mutants to the WT sequence')

# add the necessary arguments
parser.add_argument('-fluorFile','--fluorescenceFile', type=str, help='the input reconstructed fluorescence csv file')
# add the optional arguments
parser.add_argument('-outDir','--outputDir', type=str, help='the output directory')

# extract the arguments into variables
args = parser.parse_args()
fluorFile = args.fluorescenceFile
# default values for the optional arguments
outputDir = os.getcwd()
# if the optional arguments are not specified, use the default values
if args.outputDir is not None:
    outputDir = args.outputDir
    os.makedirs(outputDir, exist_ok=True)

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
    plt.savefig(f'{output_dir}/{seq}.svg')
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

def mutantTrimmingFunction(wt_df, mutant_df, seq_col):
    output_df = wt_df.copy()
    input_df = mutant_df.copy()
    output_df = output_df[output_df[seq_col].isin(input_df[seq_col])]
    return output_df

def getSimilarSequences(df, seq, fluor_col, nonmatching_aa_min):
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
    return output_df

if __name__ == '__main__':
    # read in the dataframes
    df_fluor = pd.read_csv(fluorFile)
    # get the column that contains transformed data
    fluor_col = [col for col in df_fluor.columns if 'transformed' in col][0]
    nonmatching_aa_min = 2
    matching_seq_min = 3
    wt_seq_col = 'wt_seq'
    position_col = 'position'
    
    samples = df_fluor['Sample'].unique()
    output_df = getSimilarSequences(df_fluor, wt_seq_col, fluor_col, nonmatching_aa_min)
    output_df.to_csv(f'{outputDir}/all.csv', index=False)
    output_df_2 = getSimilarSequences(df_fluor, wt_seq_col, fluor_col, 3)
    output_df_2.to_csv(f'{outputDir}/all_seqDiff_2.csv', index=False)
    output_df_3 = getSimilarSequences(df_fluor, wt_seq_col, fluor_col, 4)
    output_df_3.to_csv(f'{outputDir}/all_seqDiff_3.csv', index=False)
    output_df_4 = getSimilarSequences(df_fluor, wt_seq_col, fluor_col, 5)
    output_df_4.to_csv(f'{outputDir}/all_seqDiff_4.csv', index=False)
    
    # add mismatched position to dataframe
    output_df = addMismatchedPositions(output_df, wt_seq_col, position_col)
    output_df['wt_aa'] = output_df[position_col].apply(lambda x: x[0])
    output_df['mut_aa'] = output_df[position_col].apply(lambda x: x[-1])
    output_df['mut_position'] = output_df[position_col].apply(lambda x: x[1:-1])
    # check that the type is not WT
    output_df_mut = output_df[output_df['Type'] != 'WT']
    output_df_wt = output_df[output_df['Type'] == 'WT']
    output_df_wtlike = output_df_wt[output_df_wt['wt_seq'].isin(output_df_mut['wt_seq'])]

    # get the sequences that are similar to the wt sequence
    seq_col = 'wt_seq'
    output_wtLike_all = mutantTrimmingFunction(output_df_wt, output_df_mut, seq_col)
    output_wtLike_all.to_csv(f'{outputDir}/all_mutants.csv', index=False)
    
    output_zero = output_df[output_df['percent_wt'] == 0]
    # 
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

    # append the wt sequence to the dataframe
    wt_gtoi = output_df[output_df['Sequence'].isin(gtoi_df['wt_seq'])]
    wt_gtoi = wt_gtoi.drop_duplicates(subset=['Sequence'])
    gtoi_df = pd.concat([gtoi_df, wt_gtoi])
    gtoi_df.to_csv(f'{outputDir}/g_to_i_mutants.csv', index=False)
    

    a_df = output_df[output_df['mut_aa'] == 'A']
    gtoi_a_df = gtoi_df[gtoi_df['wt_seq'].isin(a_df['wt_seq'])]
    gtoi_a_df.to_csv(f'{outputDir}/g_to_i_AND_x_to_a.csv', index=False)
    f_df = output_df[output_df['mut_aa'] == 'F']
    gtoi_f_df = gtoi_df[gtoi_df['wt_seq'].isin(f_df['wt_seq'])]
    gtoi_f_df.to_csv(f'{outputDir}/g_to_i_AND_x_to_f.csv', index=False)
    y_df = output_df[output_df['mut_aa'] == 'Y']
    gtoi_y_df = gtoi_df[gtoi_df['wt_seq'].isin(y_df['wt_seq'])]
    gtoi_y_df.to_csv(f'{outputDir}/g_to_i_AND_x_to_y.csv', index=False)
    
    # get sequences that have a successful g83i mutation
    gtoi_df_allWts = output_df[output_df['wt_seq'].isin(gtoi_df['wt_seq'])]
    gtoi_df_allWts.to_csv(f'{outputDir}/g_to_i_test.csv', index=False)
    
    for seq in gtoi_df_allWts['wt_seq'].unique():
        df_seq = gtoi_df_allWts[gtoi_df_allWts['wt_seq'] == seq]
        # sort df by percent wt after the percent wt that is 100
        df_seq = df_seq.sort_values(by=['percent_wt'], ascending=False)
        # move the percent wt that is 100 to the top
        df_seq = pd.concat([df_seq[df_seq['percent_wt'] == 100], df_seq[df_seq['percent_wt'] != 100]])
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