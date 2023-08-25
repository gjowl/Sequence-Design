import os, sys, pandas as pd, numpy as np, matplotlib.pyplot as plt

def graphFluorescence(input_df, output_file, energy_col, fluor_col, error_col, output_dir):
    # plot the WT sequence fluorescence vs the energy
    plt.scatter(input_df[energy_col], input_df[fluor_col])
    # plot the standard deviation
    plt.errorbar(input_df[energy_col], input_df[fluor_col], yerr=input_df[error_col], fmt='o', color='black', ecolor='lightgray', elinewidth=3, capsize=0)
    plt.ylabel(fluor_col)
    plt.xlabel(energy_col)
    plt.title(f'{energy_col} vs {fluor_col}')
    # draw a line of best fit
    m, b = np.polyfit(input_df[energy_col], input_df[fluor_col], 1)
    plt.plot(input_df[energy_col], m*input_df[energy_col] + b)
    # add the equation to the plot
    plt.text(0.1, 1.12, f'y = {m:.2f}x + {b:.2f}', horizontalalignment='center', verticalalignment='center', transform=plt.gca().transAxes)
    # calculate the correlation coefficient
    corr = np.corrcoef(input_df[energy_col], input_df[fluor_col])[0,1]
    plt.text(0.1, 1.09, f'r^2 = {corr**2:.2f}', horizontalalignment='center', verticalalignment='center', transform=plt.gca().transAxes)
    plt.text(0.1, 1.06, f'n = {len(input_df)}', horizontalalignment='center', verticalalignment='center', transform=plt.gca().transAxes)
    plt.savefig(f'{output_dir}/{output_file}.png')
    plt.clf()

#def graphVsFluorescence(input_df, sample_names, cols_to_graph, fluor_col, error_col, output_dir):
#    # loop through each sample
#    for sample in sample_names:
#        df_sample = input_df[input_df['Sample'] == sample]
#        for col in cols_to_graph:
#            graphFluorescence(df_sample, f'{sample}_{col}', col, fluor_col, error_col, output_dir)

# get command line arguments
inputFile = sys.argv[1]
outputDir = sys.argv[2]

# read in the data
df_fluorAndEnergy = pd.read_csv(inputFile)

# graph the data
cols_to_graph = ['Total', 'VDWDiff', 'HBONDDiff', 'IMM1Diff', 'SasaDiff']
#cols_to_graph = ['Total']
#fluor_col = 'Percent GpA'
#error_col = 'Percent Error'
fluor_col = 'mean_transformed'
error_col = 'std_adjusted'
samples = df_fluorAndEnergy['Sample'].unique()

for col in cols_to_graph:
    #for design in df_fluorAndEnergy['Design'].unique():
    #    df_design = df_fluorAndEnergy[df_fluorAndEnergy['Design'] == design]
    #    output_dir = f'{outputDir}/{design}'
    #os.makedirs(output_dir, exist_ok=True)
    for seq in df_fluorAndEnergy['wt_seq'].unique():
        df_seq = df_fluorAndEnergy[df_fluorAndEnergy['wt_seq'] == seq]
        df_seq = df_seq.drop_duplicates(subset=['Sequence'])
        if len(df_seq) < 5:
            continue
        #graphFluorescence(df_seq, f'{sample}_{col}', col, fluor_col, error_col, output_dir)
        output_file = f'{seq}'
        corr = np.corrcoef(df_seq[col], df_seq[fluor_col])[0,1]**2
        if abs(corr) < 0.5:
            continue
        # get the design 
        design = df_seq['Sample'].unique()[0]
        output_dir = f'{outputDir}/{design}'
        output_dir = f'{output_dir}/{col}'
        os.makedirs(output_dir, exist_ok=True)
        graphFluorescence(df_seq, output_file, col, fluor_col, error_col, output_dir)
        # add in a limit for r^2 value
    #    os.makedirs(design_dir, exist_ok=True)
    #    graphVsFluorescence(df_design, samples, cols_to_graph, fluor_col, error_col, design_dir)
        

# TODO: print the energy graphs for sequences based on the categories I give them
# example: some mutants higher than WT, some lower than WT, some similar to WT
# all mutants lower than wt