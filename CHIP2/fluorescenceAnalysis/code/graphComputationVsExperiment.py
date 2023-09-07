import os, sys, pandas as pd, numpy as np, matplotlib.pyplot as plt
from scipy.stats import linregress

colors = ['mediumseagreen', 'navajowhite', 'darkslateblue', 'brown', 'pink', 'gray', 'olive', 'cyan']
def graphFluorescence(input_df, output_file, energy_col, fluor_col, error_col, output_dir, useColors=False):
    # loop through the samples of the input_df
    if useColors:
        for sample, i in zip(input_df['Sample'].unique(), range(len(input_df['Sample'].unique()))):
            df_sample = input_df[input_df['Sample'] == sample]
            # plot the WT sequence fluorescence vs the energy
            plt.scatter(df_sample[energy_col], df_sample[fluor_col], color=colors[i], label=sample)
            # plot the standard deviation
            plt.errorbar(df_sample[energy_col], df_sample[fluor_col], yerr=df_sample[error_col], fmt='o', color=colors[i], ecolor='lightgray', elinewidth=3, capsize=0)
            # add a legend
            plt.legend(loc='upper left', bbox_to_anchor=(1,1))
    else:
        # plot the WT sequence fluorescence vs the energy
        plt.scatter(input_df[energy_col], input_df[fluor_col])
        # plot the standard deviation
        plt.errorbar(input_df[energy_col], input_df[fluor_col], yerr=input_df[error_col], fmt='o', color='black', ecolor='lightgray', elinewidth=3, capsize=0)
    ## plot the standard deviation
    #plt.errorbar(input_df[energy_col], input_df[fluor_col], yerr=input_df[error_col], fmt='o', color='black', ecolor='lightgray', elinewidth=3, capsize=0)
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
    # make sure the minimum y value is 0, and set the ylim top to 100 if it is less than 100
    plt.ylim(bottom=0)
    #if plt.ylim()[1] < 1:
    #    plt.ylim(top=1)
    #slope, intercept, r_value, p_value, std_err = linregress(input_df[energy_col], input_df[fluor_col])
    #plt.text(0.1, 1.03, f'p = {p_value:.5f}', horizontalalignment='center', verticalalignment='center', transform=plt.gca().transAxes)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/{output_file}.png')
    plt.clf()

def graphVsFluorescence(input_df, sample_names, cols_to_graph, fluor_col, error_col, output_dir):
    # loop through each sample
    for sample in sample_names:
        df_sample = input_df[input_df['Sample'] == sample]
        if len(df_sample) > 1:
            for col in cols_to_graph:
                graphFluorescence(df_sample, f'{sample}_{col}', col, fluor_col, error_col, output_dir)
                df_col = df_sample[col].copy()
        df_sample.to_csv(f'{output_dir}/{sample}.csv', index=False)

# get command line arguments
inputFile = sys.argv[1]
outputDir = sys.argv[2]

# read in the data
df_fluorAndEnergy = pd.read_csv(inputFile)

# graph the data
cols_to_graph = ['Total', 'VDWDiff', 'HBONDDiff', 'IMM1Diff', 'SasaDiff']
#fluor_col = 'Percent GpA'
#error_col = 'Percent Error'
#fluor_col = 'mean_transformed'
fluor_col = [col for col in df_fluorAndEnergy.columns if 'transformed' in col][0]
error_col = 'std_adjusted'
#fluor_col = 'Fluorescence'
#error_col = 'FluorStdDev'
samples = df_fluorAndEnergy['Sample'].unique()
# check if there is a design column
if 'Design' in df_fluorAndEnergy.columns:
    for design in df_fluorAndEnergy['Design'].unique():
        df_design = df_fluorAndEnergy[df_fluorAndEnergy['Design'] == design].copy()
        df_design.drop_duplicates(subset='Sequence', keep='first', inplace=True)
        design_dir = outputDir + '/' + design
        os.makedirs(design_dir, exist_ok=True)
        graphFluorescence(df_design, f'all_{design}', 'Total', fluor_col, error_col, design_dir, True)
        graphVsFluorescence(df_design, samples, cols_to_graph, fluor_col, error_col, design_dir)

for col in cols_to_graph:
    df_fluorAndEnergy.drop_duplicates(subset='Sequence', keep='first', inplace=True)
    graphFluorescence(df_fluorAndEnergy, f'all_{col}', col, fluor_col, error_col, outputDir, True)


