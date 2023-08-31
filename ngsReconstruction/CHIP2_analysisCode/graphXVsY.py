import os, sys, pandas as pd, numpy as np, matplotlib.pyplot as plt

def graphXVsY(input_df, output_file, x_col, y_col, error_col, output_dir):
    # plot the WT sequence fluorescence vs the energy
    plt.scatter(input_df[x_col], input_df[y_col])
    # plot the standard deviation
    plt.errorbar(input_df[x_col], input_df[y_col], yerr=input_df[error_col], fmt='o', color='black', ecolor='lightgray', elinewidth=3, capsize=0)
    plt.ylabel(y_col)
    plt.xlabel(x_col)
    plt.title(f'{x_col} vs {y_col}')
    # draw a line of best fit
    m, b = np.polyfit(input_df[x_col], input_df[y_col], 1)
    plt.plot(input_df[x_col], m*input_df[x_col] + b)
    # add the equation to the plot
    plt.text(0.1, 1.12, f'y = {m:.2f}x + {b:.2f}', horizontalalignment='center', verticalalignment='center', transform=plt.gca().transAxes)
    # calculate the correlation coefficient
    corr = np.corrcoef(input_df[x_col], input_df[y_col])[0,1]
    plt.text(0.1, 1.09, f'r^2 = {corr**2:.2f}', horizontalalignment='center', verticalalignment='center', transform=plt.gca().transAxes)
    plt.text(0.1, 1.06, f'n = {len(input_df)}', horizontalalignment='center', verticalalignment='center', transform=plt.gca().transAxes)
    plt.savefig(f'{output_dir}/{output_file}.png')
    plt.clf()

# get command line arguments
inputFile = sys.argv[1]
outputFile = sys.argv[2]
outputDir = sys.argv[3]

os.makedirs(name=outputDir, exist_ok=True)

# read in the data
df_input = pd.read_csv(inputFile)

# graph the data
xaxis = 'Total'
yaxis = 'deltaG'
error_col = 'std_deltaG'

graphXVsY(df_input, outputFile, xaxis, yaxis, error_col, outputDir)