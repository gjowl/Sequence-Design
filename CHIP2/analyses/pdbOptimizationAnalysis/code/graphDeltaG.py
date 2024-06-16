import os, sys, pandas as pd, numpy as np, matplotlib.pyplot as plt, argparse, scipy.stats as stats, seaborn as sns
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

# defaults for the plotting
colors = ['dimgrey', 'darkorange', 'blueviolet', 'brown', 'pink', 'gray', 'olive', 'cyan']
font = 'Arial'
axis_font_size = 16
text_font_size = 18
title_font_size = 20

# Functions
def plotHistogram(df, bins, lowerLim, numBins, colors, outputDir):
    sample = df['Sample'].values[0]
    plt.hist(df['deltaG'], bins=bins, color=colors[i], edgecolor='black', label=f'{sample} ({len(df)})')
    # set the limits of the x-axis
    plt.xlim(lowerLim, 0)
    plt.legend()
    plt.xlabel('ΔG', fontsize=title_font_size, fontname=font)
    plt.ylabel('Frequency', fontsize=title_font_size, fontname=font)
    # set the font size of the x and y axis
    plt.xticks(fontsize=axis_font_size, fontname=font)
    plt.yticks(fontsize=axis_font_size, fontname=font)
    # set the font size of the title
    plt.title('Histogram of ΔG', fontsize=title_font_size, fontname=font)
    plt.tight_layout()
    plt.savefig(f'{outputDir}/{sample}_deltaG_hist.png')
    plt.savefig(f'{outputDir}/{sample}_deltaG_hist.svg')
    plt.clf()

def plotOverlayedHistogram(df_input, bins, lowerLim, numBins, colors, outputDir):
    plt.figure()
    for sample, i in zip(df_input['Sample'].unique(), range(len(df_input['Sample'].unique()))):
        df_sample = df_input[df_input['Sample'] == sample]
        # plot a histogram of the deltaG values with edges black
        sns.histplot(df_sample['deltaG'], bins=bins, color=colors[i], edgecolor='black', label=f'{sample} ({len(df_sample)})', kde=True)
    # add in the legend
    plt.legend()
    plt.xlabel('ΔG', fontsize=title_font_size, fontname=font)
    plt.ylabel('Frequency', fontsize=title_font_size, fontname=font)
    # set the font size of the x and y axis
    plt.xticks(fontsize=axis_font_size, fontname=font)
    plt.yticks(fontsize=axis_font_size, fontname=font)
    # put the yaxis on the right side
    plt.gca().yaxis.tick_right()
    plt.gca().yaxis.set_label_position("right")
    plt.title('Dimerization Density Histogram', fontsize=title_font_size, fontname=font)
    plt.tight_layout()
    plt.savefig(f'{outputDir}/overlay_deltaG_hist.png')
    plt.savefig(f'{outputDir}/overlay_deltaG_hist.svg')
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
    # set the lower limit of the x-axis for deltaG plots
    lowerLim = round(df_input['deltaG'].min()-1, 1) 
    # set the bins separated by 0.5
    bins = np.arange(lowerLim, 0, 0.5)
    numBins = len(bins)

    # plot the scatterplots
    for xaxis in xaxes:
        outputFile = f'{xaxis}_vs_{yaxis}'
        png_dir = f'{outputDir}/png'
        svg_dir = f'{outputDir}/svg'
        os.makedirs(name=png_dir, exist_ok=True)
        os.makedirs(name=svg_dir, exist_ok=True)
        plotScatterplot(df_input, xaxis, yaxis, error_col, regression_degree, outputFile, png_dir, svg_dir, True) # function from analyzeData.py

    for sample, i in zip(df_input['Sample'].unique(), range(len(df_input['Sample'].unique()))):
        df_sample = df_input[df_input['Sample'] == sample]
        for xaxis in xaxes:
            outputFile = f'{xaxis}_vs_{yaxis}'
            sample_dir = f'{outputDir}/{sample}'
            png_dir = f'{sample_dir}/png'
            svg_dir = f'{sample_dir}/svg'
            os.makedirs(name=png_dir, exist_ok=True)
            os.makedirs(name=svg_dir, exist_ok=True)
            if xaxis == 'IMM1Diff': # sets the limits to be positive for IMM1Diff
                plotScatterplotSingle(df_sample, sample, xaxis, yaxis, error_col, regression_degree, outputFile, png_dir, svg_dir, sampleType=sample, color=colors[i], xlowLim=0, xhighLim=60, ylowLim=-6.5, yhighLim=0) # function from analyzeData.py
            else:
                plotScatterplotSingle(df_sample, sample, xaxis, yaxis, error_col, regression_degree, outputFile, png_dir, svg_dir, sampleType=sample, color=colors[i], xlowLim=-60, xhighLim=0, ylowLim=-6.5, yhighLim=0) # function from analyzeData.py
        # plot a histogram of the deltaG values with edges black
        plotHistogram(df_sample, bins, lowerLim, numBins, colors, outputDir)

    # create an overlayed histogram of the deltaG values
    plotOverlayedHistogram(df_input, bins, lowerLim, numBins, colors, outputDir)

    # create an overlayed histogram of the deltaG values by percentage
    plt.figure()
    for sample, i in zip(df_input['Sample'].unique(), range(len(df_input['Sample'].unique()))):
        df_sample = df_input[df_input['Sample'] == sample]
        # get the counts per bin
        counts, bins = np.histogram(df_sample['deltaG'], bins=bins)
        # get the percentage of counts per bin
        percentage = counts/len(df_sample)*100
        df = pd.DataFrame({'percentage': percentage, 'bins': bins[:-1]})
        # make a histogram of the percentage of counts per bin
        sns.kdeplot(df_sample['deltaG'], color=colors[i], label=f'{sample} ({len(df_sample)})')
    # set the limits of the x-axis
    plt.xlim(lowerLim, 0)
    plt.legend()
    plt.xlabel('ΔG', fontsize=title_font_size, fontname=font)
    plt.ylabel(f'% Frequency', fontsize=title_font_size, fontname=font)
    # put the yaxis on the right side
    plt.gca().yaxis.tick_right()
    plt.gca().yaxis.set_label_position("right")
    # set the yaxis to be a percentage by multiplying by 100
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x*100:.0f}%'))
    # set the font size of the x and y axis
    plt.xticks(fontsize=axis_font_size, fontname=font)
    plt.yticks(fontsize=axis_font_size, fontname=font)
    plt.title('Dimerization Density Histogram', fontsize=title_font_size, fontname=font)
    plt.tight_layout()
    plt.savefig(f'{outputDir}/overlay_deltaG_hist_percent.png')
    plt.savefig(f'{outputDir}/overlay_deltaG_hist_percent.svg')
    plt.clf()

