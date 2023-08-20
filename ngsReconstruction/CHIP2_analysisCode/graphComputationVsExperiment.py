
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
    plt.text(0.5, 0.5, f'y = {m:.2f}x + {b:.2f}', horizontalalignment='center', verticalalignment='center', transform=plt.gca().transAxes)
    # calculate the correlation coefficient
    corr = np.corrcoef(input_df[energy_col], input_df[fluor_col])[0,1]
    plt.text(0.5, 0.4, f'r = {corr:.2f}', horizontalalignment='center', verticalalignment='center', transform=plt.gca().transAxes)
    plt.savefig(f'{output_dir}/{output_file}.png')
    plt.clf()

def graphVsFluorescence(input_df, sample_names, cols_to_graph, fluor_col, error_col, output_dir):
    # loop through each sample
    for sample in sample_names:
        df_sample = input_df[input_df['Sample'] == sample]
        for col in cols_to_graph:
            graphFluorescence(df_sample, f'{sample}_{col}', col, fluor_col, error_col, output_dir)

# get command line arguments
inputFile = sys.argv[1]
outputDir = sys.argv[2]

# read in the data
df_fluorAndEnergy = pd.read_csv(inputFile)

# graph the data
cols_to_graph = ['Total', 'VDWDiff', 'HBONDDiff', 'IMM1Diff', 'SasaDiff']
#fluor_col = 'Percent GpA'
#error_col = 'Percent Error'
fluor_col = 'mean_transformed'
error_col = 'std_adjusted'
samples = df_fluorAndEnergy['Sample'].unique()
for design in df_fluorAndEnergy['Design'].unique():
    df_design = df_fluorAndEnergy[df_fluorAndEnergy['Design'] == design]
    design_dir = outputDir + '/' + design
    os.makedirs(design_dir, exist_ok=True)
    graphVsFluorescence(df_design, samples, cols_to_graph, fluor_col, error_col, design_dir)
