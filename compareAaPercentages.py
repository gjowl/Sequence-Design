import os, sys, pandas as pd, matplotlib.pyplot as plt, numpy as np, argparse

# initialize the parser
parser = argparse.ArgumentParser(description='Calculated the single AA and multiple AA composition of a sequence file')
parser.add_argument('-seqFile','--sequenceFile', type=str, help='the input file of sequences to be analyzed')
parser.add_argument('-designFile','--designFile', type=str, help='the input file of sequences to be analyzed')
# optional arguments
parser.add_argument('-outputDir','--outputDir', type=str, help='the output directory')

# extract the arguments into variables
args = parser.parse_args()
sequenceFile = args.sequenceFile
designFile = args.designFile
outputDir = 'AAComposition'
if args.outputDir is None:
    outputDir = args.outputDir
outputDir = args.outputDir
os.makedirs(outputDir, exist_ok=True)

if __name__ == "__main__":
    # read in the data file (extracted data from the pdb files)
    sequence_df = pd.read_csv(sequenceFile)
    design_df = pd.read_csv(designFile)

    # get the name of the design_df
    designName = designFile.split('/')[-1].split('.')[0]

    # sort by Percentage
    sequence_df = sequence_df.sort_values(by='Percentage', ascending=False)
    design_df = design_df.sort_values(by='Percentage', ascending=False)
    
    # loop through the rows in the sequence_df
    for index, row in sequence_df.iterrows():
        # get the amino acid pair column
        aa = str(row['Amino Acid Pair'])
        # put the pair in alphabetical order
        aa = ''.join(sorted(aa))
        # replace the pair with the alphabetized pair for this pair
        sequence_df.at[index, 'Amino Acid Pair'] = aa

    for index, row in design_df.iterrows():
        # get the amino acid pair column
        aa = str(row['Amino Acid Pair'])
        # put the pair in alphabetical order
        aa = ''.join(sorted(aa))
        # replace the pair with the alphabetized pair for this pair
        design_df.at[index, 'Amino Acid Pair'] = aa
    
    sequence_df = sequence_df.sort_values(by='Amino Acid Pair', ascending=False)
    design_df = design_df.sort_values(by='Amino Acid Pair', ascending=False)
    print(sequence_df)

    # combine values for the same pairs, getting average of Percentage and sum of Count
    sequence_df = sequence_df.groupby('Amino Acid Pair').agg({'Percentage': 'mean', 'Count': 'sum', 'Unique Sequences': 'sum'}).reset_index()
    design_df = design_df.groupby('Amino Acid Pair').agg({'Percentage': 'mean', 'Count': 'sum', 'Unique Sequences': 'sum'}).reset_index()

    # check if any pairs found in sequence_df are not in design_df
    missingPairs = sequence_df[~sequence_df['Amino Acid Pair'].isin(design_df['Amino Acid Pair'])]

    # add those pairs to the design_df with a Percentage of 0
    missingPairs['Percentage'] = 0
    missingPairs['Count'] = 0
    missingPairs['Unique Sequences'] = 0
    design_df = pd.concat([design_df, missingPairs])

    # sort by pair and reset index
    design_df = design_df.reset_index(drop=True)
    sequence_df = sequence_df.reset_index(drop=True)

    # add the Percentage of the sequence_df to the design_df
    design_df['AACompositionCount'] = sequence_df['Count']
    design_df['AACompositionPercentage'] = sequence_df['Percentage']
    # get the pairs with the highest difference in Percentage
    design_df['Percentage Difference'] = design_df['Percentage'] - sequence_df['Percentage']
    design_df = design_df.sort_values(by='Percentage Difference', ascending=False)
    design_df.to_csv(f'{outputDir}/percDiff.csv', index=False)

    # keep only the pairs with a count > 10
    limit = 10
    design_df = design_df[design_df['Count'] > limit]
    design_df.to_csv(f'{outputDir}/percDiff_count{limit}.csv', index=False)

    # keep the 10 largest differences in Percentage by using the absolute value
    design_df['Range'] = design_df['Percentage Difference'].abs()
    top10 = design_df.nlargest(10, 'Range')

    # plot the data on a bar chart
    fig, ax = plt.subplots()
    ax.bar(top10['Amino Acid Pair'], top10['Percentage Difference'], color='b')
    ax.set_ylabel('% Difference', size=12)
    ax.set_xlabel('Amino Acid Pair', size=12)
    ax.set_title(f'Percentage Difference of Amino Acid Pairs in {designName}', size=14)
    # set the ytick size
    plt.yticks(size=14)
    # set the xtick size
    plt.xticks(size=14)
    plt.tight_layout()
    # set the y-limit
    ax.set_ylim(-45, 35)
    plt.savefig(f'{outputDir}/{designName}_percDiff.png')
    plt.savefig(f'{outputDir}/{designName}_percDiff.svg')
    plt.close()


