import os, sys, pandas as pd, numpy as np, matplotlib.pyplot as plt
from scipy.stats import linregress

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
    # make sure the minimum y value is 0, and set the ylim top to 100 if it is less than 100
    plt.ylim(bottom=0)
    #if plt.ylim()[1] < 100:
    #    plt.ylim(top=100)
    # get a p-value for the correlation
    #slope, intercept, r_value, p_value, std_err = linregress(input_df[energy_col], input_df[fluor_col])
    #p_limit = 0.05
    #if p_value < p_limit:
    #    plt.text(0.1, 1.03, f'p < {p_limit:.5f}', horizontalalignment='center', verticalalignment='center', transform=plt.gca().transAxes)
    #else:
    #    plt.text(0.1, 1.03, f'p = {p_value:.5f}', horizontalalignment='center', verticalalignment='center', transform=plt.gca().transAxes)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/{output_file}.png')
    plt.clf()

# get command line arguments
inputFile = sys.argv[1]
outputDir = sys.argv[2]

os.makedirs(name=outputDir, exist_ok=True)

# read in the data
df_fluorAndEnergy = pd.read_csv(inputFile)

# graph the data
cols_to_graph = ['Total', 'VDWDiff', 'HBONDDiff', 'IMM1Diff', 'SasaDiff']
#cols_to_graph = ['CHARMM_IMM1', 'CHARMM_IMM1REF', 'CHARMM_VDW', 'Dimer']
#cols_to_graph = ['Total']
#fluor_col = 'Percent GpA'
#error_col = 'Percent Error'
#fluor_col = 'mean_transformed'
fluor_col = [col for col in df_fluorAndEnergy.columns if 'transformed' in col][0]
error_col = 'std_adjusted'
#fluor_col = 'Fluorescence'
#error_col = 'FluorStdDev'
samples = df_fluorAndEnergy['Sample'].unique()

# loop through the columns to graph
for col in cols_to_graph:
    # loop through the sequences
    for seq in df_fluorAndEnergy['wt_seq'].unique():
        df_seq = df_fluorAndEnergy[df_fluorAndEnergy['wt_seq'] == seq]
        # remove any duplicates
        df_seq = df_seq.sort_values(by=['Total'])
        df_seq = df_seq.drop_duplicates(subset=['Sequence'], keep='first')
        if len(df_seq) < 5:
            continue
        #graphFluorescence(df_seq, f'{sample}_{col}', col, fluor_col, error_col, output_dir)
        output_file = f'{seq}'
        corr = np.corrcoef(df_seq[col], df_seq[fluor_col])[0,1]**2
        if abs(corr) < 0.4:
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
        
#for col in cols_to_graph:
#    for sample in df_fluorAndEnergy['Sample'].unique():
#        df_sample = df_fluorAndEnergy[df_fluorAndEnergy['Sample'] == sample]
#        output_dir = f'{outputDir}/{sample}'
#        # get max value in the col
#        max_value = df_sample[col].max()
#        limit = 10000000
#        if max_value > limit:
#            # set all values over that to 100000
#            df_sample[col] = df_sample[col].apply(lambda x: limit if x > limit else x)
#        graphFluorescence(df_sample, f'all_{col}', col, fluor_col, error_col, outputDir)

# TODO: print the energy graphs for sequences based on the categories I give them
# example: some mutants higher than WT, some lower than WT, some similar to WT
# all mutants lower than wt