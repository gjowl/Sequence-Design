import os, sys, pandas as pd, numpy as np, matplotlib.pyplot as plt, argparse, scipy.stats as stats
from analyzeData import plotScatterplotSingle, plotScatterplot

# initialize the parser
parser = argparse.ArgumentParser(description='Graphs data as scatterplots against deltaG')

# add the necessary arguments
parser.add_argument('-inFile','--inputFile', type=str, help='the input csv file')
parser.add_argument('-outDir','--outputDir', type=str, help='the output directory')

# extract the arguments into variables
args = parser.parse_args()
inputFile = args.inputFile
outputDir = args.outputDir
os.makedirs(name=outputDir, exist_ok=True)

colors = ['dimgrey', 'darkorange', 'blueviolet', 'brown', 'pink', 'gray', 'olive', 'cyan']
def graphXVsY(input_df, output_file, x_col, y_col, error_col, png_dir, svg_dir):
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
    plt.savefig(f'{png_dir}/{output_file}.png')
    plt.savefig(f'{svg_dir}/{output_file}.svg')
    plt.clf()

if __name__ == '__main__':
    # read in the data
    df_input = pd.read_csv(inputFile)

    # remove data with total energy greater than 0
    df_input = df_input[df_input['Total'] < 0]
    df_input = df_input[df_input['deltaG'] < 0]

    # variables for graphing the data
    xaxes = ['Total', 'VDWDiff', 'HBONDDiff', 'IMM1Diff']
    yaxis = 'deltaG'
    error_col = 'std_deltaG'
    regression_degree = 1
    lowerLim = df_input['deltaG'].min()
    # set the bins separated by 0.5
    bins = np.arange(lowerLim-0.5, 0, 0.5)
    numBins = len(bins)

    #graphXVsY(df_input, outputFile, xaxis, yaxis, error_col, outputDir)
    for xaxis in xaxes:
        outputFile = f'{xaxis}_vs_{yaxis}'
        png_dir = f'{outputDir}/png'
        svg_dir = f'{outputDir}/svg'
        os.makedirs(name=png_dir, exist_ok=True)
        os.makedirs(name=svg_dir, exist_ok=True)
        plotScatterplot(df_input, xaxis, yaxis, error_col, regression_degree, outputFile, png_dir, svg_dir, True)

    for sample, i in zip(df_input['Sample'].unique(), range(len(df_input['Sample'].unique()))):
        df_sample = df_input[df_input['Sample'] == sample]
        for xaxis in xaxes:
            outputFile = f'{xaxis}_vs_{yaxis}'
            sample_dir = f'{outputDir}/{sample}'
            png_dir = f'{sample_dir}/png'
            svg_dir = f'{sample_dir}/svg'
            os.makedirs(name=png_dir, exist_ok=True)
            os.makedirs(name=svg_dir, exist_ok=True)
            if xaxis == 'IMM1Diff':
                plotScatterplotSingle(df_sample, sample, xaxis, yaxis, error_col, regression_degree, outputFile, png_dir, svg_dir, sampleType=sample, color=colors[i], xlowLim=0, xhighLim=60, ylowLim=-6.5, yhighLim=0)
            else:
                plotScatterplotSingle(df_sample, sample, xaxis, yaxis, error_col, regression_degree, outputFile, png_dir, svg_dir, sampleType=sample, color=colors[i], xlowLim=-60, xhighLim=0, ylowLim=-6.5, yhighLim=0)
        # plot a histogram of the deltaG values with edges black
        plt.hist(df_sample['deltaG'], bins=bins, color=colors[i], edgecolor='black', label=f'{sample} ({len(df_sample)})')
        # set the limits of the x-axis
        plt.xlim(lowerLim-0.5, 0)
        plt.legend()
        plt.xlabel('deltaG')
        plt.ylabel('Frequency')
        plt.title('Histogram of deltaG values')
        plt.savefig(f'{outputDir}/{sample}_deltaG_hist.png')
        plt.savefig(f'{outputDir}/{sample}_deltaG_hist.svg')

    # create an overlayed histogram of the deltaG values
    plt.figure()
    for sample, i in zip(df_input['Sample'].unique(), range(len(df_input['Sample'].unique()))):
        df_sample = df_input[df_input['Sample'] == sample]
        # plot a histogram of the deltaG values with edges black
        plt.hist(df_sample['deltaG'], bins=bins, color=colors[i], edgecolor='black', alpha=0, label=f'{sample} ({len(df_sample)})')
        # set the limits of the x-axis
        plt.xlim(lowerLim-0.5, 0)
        # get the xaxis length
        xaxis_length = plt.gca().get_xlim()[1] - plt.gca().get_xlim()[0]
        # plot the kde of the deltaG values (https://stackoverflow.com/questions/59738337/how-to-draw-a-matching-bell-curve-over-a-histogram)
        binwidth = xaxis_length / numBins
        scale_factor = len(df_sample) * binwidth
        kde = stats.gaussian_kde(df_sample['deltaG'])
        plt.plot(np.linspace(lowerLim-0.5, 0, 100), kde(np.linspace(lowerLim-0.5, 0, 100))*scale_factor, color=colors[i])
        # remove the histogram bars
        plt.gca().patches[0].set_visible(False)
    # add in the legend
    plt.legend()
    plt.xlabel('deltaG')
    plt.ylabel('Frequency')
    plt.title('Histogram of deltaG values')
    plt.savefig(f'{outputDir}/overlay_deltaG_hist.png')
    plt.savefig(f'{outputDir}/overlay_deltaG_hist.svg')
    
    