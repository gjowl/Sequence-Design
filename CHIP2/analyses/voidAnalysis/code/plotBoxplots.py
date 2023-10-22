import os, sys, pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns

def plotPercentSeqs(input_df, col, output_dir):
    sns.set_style("whitegrid")
    sns.boxplot(x="Sample", y=col,data=input_df, color='green', fliersize=2)
    sns.swarmplot(x="Sample", y=col, data=input_df, color='0', dodge=True, size=2)
    # sort by sample
    input_df = input_df.sort_values(by=['Sample'])
    #calculate_pvalues(input_df)
    for i, sample in enumerate(input_df['Sample'].unique()):
        plt.text(i, 1.65, len(input_df[input_df['Sample'] == sample]), ha='left')
    #    # separate the dataframe by mutant and wt
    #    df_wt, df_mutant = input_df[input_df['Type'] == 'WT'], input_df[input_df['Type'] == 'Mutant']
    #    plt.text(i-.25, -.07, len(df_wt[df_wt['Sample'] == sample]), ha='left')
    #    plt.text(i+.25, -.07, len(df_mutant[df_mutant['Sample'] == sample]), ha='right')
    # remove the legend
    plt.legend([],[], frameon=False)
    plt.xlabel('Sample')
    plt.ylabel('Percent GpA')
    # set the y axis limits
    # TODO: add the pvalue to the plot
    plt.ylim(bottom=0)
    plt.ylim(top=1.6)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/percentSeqs_{col}.png')
    plt.clf()

# read in the command line arguments
inputFile = sys.argv[1]
outputDir = sys.argv[2]

# read in the input files
df = pd.read_csv(inputFile, sep=',')
cols = ['PercentGpA_transformed', 'PercentGpA_Design']

for col in cols:
    if col == 'PercentGpA_Design':
        # keep only unique sequences
        df_sample = df.drop_duplicates(subset=['Sequence'])
        plotPercentSeqs(df_sample, col, outputDir)
    else:
        plotPercentSeqs(df, col, outputDir)
