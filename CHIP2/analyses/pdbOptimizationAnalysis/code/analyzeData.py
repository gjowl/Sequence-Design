import os, sys, pandas as pd, matplotlib.pyplot as plt, numpy as np, argparse
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

# initialize the parser
parser = argparse.ArgumentParser(description='Plots the data into scatterplots')

# add the necessary arguments
parser.add_argument('-inFile','--inputFile', type=str, help='the input csv file')
parser.add_argument('-outDir','--outputDir', type=str, help='the output directory')
# add the optional arguments
parser.add_argument('-percentCutoff','--percentCutoff', type=float, help='the cutoff for the percent GpA')

# extract the arguments into variables
args = parser.parse_args()
inputFile = args.inputFile
outputDir = args.outputDir
percentGpA_cutoff = 0
# default values for the optional arguments
if args.percentCutoff is not None:
    percentGpA_cutoff = args.percentCutoff
# make the output directory if it doesn't exist and the png and svg subdirectories
os.makedirs(outputDir, exist_ok=True)

colors = ['dimgrey', 'darkorange', 'mediumorchid', 'brown', 'pink', 'gray', 'olive', 'cyan']
# plot scatterplot function
#TODO: could get a standard deviation for the x axis energies now that I have multiple repack energies
def plotScatterplot(input_df, xAxis, yAxis, yStd, regression_degree, output_title, png_dir, svg_dir, sampleType=0, color=0):
    for sample, i in zip(input_df['Sample'].unique(), range(len(input_df['Sample'].unique()))):
        df_sample = input_df[input_df['Sample'] == sample]
        # plot the WT sequence fluorescence vs the energy
        plt.scatter(df_sample[xAxis], df_sample[yAxis], color=colors[i], label=sample, s=5)
        # plot the standard deviation
        plt.errorbar(df_sample[xAxis], df_sample[yAxis], yerr=df_sample[yStd], fmt='o', color=colors[i], ecolor='dimgray', elinewidth=1, capsize=2, markersize=4)
    plt.legend(loc='upper left', bbox_to_anchor=(1,1))
    plt.text(0.99, 1.10, f'N = {len(input_df)}', transform=plt.gca().transAxes, fontsize=14, verticalalignment='top', horizontalalignment='right')
    plt.xlabel(xAxis)
    plt.ylabel(yAxis)
    plt.title(f'{xAxis} vs {yAxis}')
    plt.tight_layout()

    # check if the input_df[xAxis] is empty
    if input_df[xAxis].empty:
        plt.close()
        plt.clf()
        return

    plt.savefig(f'{png_dir}/scatter_{output_title}.png')
    plt.savefig(f'{svg_dir}/scatter_{output_title}.svg')
    
    # add a line of best fit and an r^2 value
    m, b = np.polyfit(input_df[xAxis], input_df[yAxis], regression_degree)
    plt.plot(input_df[xAxis], m*input_df[xAxis] + b, color='red')
    # add the r^2 value to the top left of the plot
    r2 = np.corrcoef(input_df[xAxis], input_df[yAxis])[0,1]**2
    plt.text(0.01, 1.10, f'r^2 = {r2:.2f}', transform=plt.gca().transAxes, fontsize=14, verticalalignment='top')
    plt.savefig(f'{png_dir}/scatterRegression_{output_title}_{regression_degree}.png')
    plt.savefig(f'{svg_dir}/scatterRegression_{output_title}_{regression_degree}.svg')
    # remove the line of best fit
    plt.gca().lines.pop()
    # remove the r^2 value
    plt.gca().texts.pop()
    plt.close()
    plt.clf()

def plotScatterplotSingle(input_df, sample, xAxis, yAxis, yStd, regression_degree, output_title, png_dir, svg_dir, sampleType=0, color=0, xlowLim=-60, xhighLim=0, ylowLim=0, yhighLim=1.75):
    # check if the yaxis highest value is above the yhighLim
    if input_df[yAxis].max() > yhighLim:
        # get 1/10th of the highest value
        yhighLim_10th = input_df[yAxis].max() / 10
        yhighLim = input_df[yAxis].max() + yhighLim_10th
    df_sample = input_df[input_df['Sample'] == sample]
    # plot the WT sequence fluorescence vs the energy
    plt.scatter(df_sample[xAxis], df_sample[yAxis], color=color, label=sample, s=5)
    # plot the standard deviation
    plt.errorbar(df_sample[xAxis], df_sample[yAxis], yerr=df_sample[yStd], fmt='o', color=color, ecolor='dimgray', elinewidth=1, capsize=2, markersize=4)
    plt.text(0.99, 1.10, f'N = {len(df_sample)}', transform=plt.gca().transAxes, fontsize=14, verticalalignment='top', horizontalalignment='right')
    plt.xlabel(xAxis)
    plt.ylabel(yAxis)
    # set the y axis limits
    plt.ylim(ylowLim, yhighLim)
    # set the x axis limits
    plt.xlim(xlowLim, xhighLim)
    plt.title(f'{xAxis} vs {yAxis}')
    plt.tight_layout()
    # check if the input_df[xAxis] is empty
    if df_sample[xAxis].empty:
        plt.close()
        plt.clf()
        return
    plt.savefig(f'{png_dir}/scatter_{output_title}.png')
    plt.savefig(f'{svg_dir}/scatter_{output_title}.svg')
    # add a line of best fit and an r^2 value
    m, b = np.polyfit(df_sample[xAxis], df_sample[yAxis], regression_degree)
    plt.plot(df_sample[xAxis], m*df_sample[xAxis] + b, color='red')
    # add the r^2 value to the top left of the plot
    r2 = np.corrcoef(df_sample[xAxis], df_sample[yAxis])[0,1]**2
    plt.text(0.01, 1.10, f'r^2 = {r2:.2f}', transform=plt.gca().transAxes, fontsize=14, verticalalignment='top')
    plt.savefig(f'{png_dir}/scatterRegression_{output_title}_{regression_degree}.png')
    plt.savefig(f'{svg_dir}/scatterRegression_{output_title}_{regression_degree}.svg')
    # remove the line of best fit
    plt.gca().lines.pop()
    # remove the r^2 value and equation
    plt.gca().texts.pop()
    plt.close()
    plt.clf()

def addEnergyDifferencesToDataframe(input_df, cols):
    for col in cols:
        #df[f'{col}Diff'] = df[f'{col}DimerPreOptimize'] - df[f'{col}Monomer']
        #input_df[f'{col}Diff'] = input_df[f'{col}DimerOptimize'] - df[f'{col}Monomer']
        input_df[f'{col}Diff'] = input_df[f'{col}Optimize'] - df[f'{col}Monomer']
    return input_df

if __name__ == '__main__':
    # read in the data file
    df = pd.read_csv(inputFile)

    #xAxis = 'TotalPreOptimize'
    xAxis = 'Total'
    # check if toxgreen_fluor is in the dataframe
    if 'toxgreen_fluor' in df.columns:
        yAxis = 'toxgreen_fluor'
        yStd = 'toxgreen_std'
    else:
        yAxis = 'PercentGpA'
        yStd = 'PercentStd'
    
    # only keep sequences with the lowest total energy
    df = df.sort_values(by=[xAxis], ascending=True)
    df = df.drop_duplicates(subset=['Sequence'], keep='first')
    # move the sequence column to the front of the dataframe
    cols = df.columns.tolist()
    cols.insert(0, cols.pop(cols.index('Sequence')))

    # hardcoding the regression degree
    regression_degree = 1

    # TRIMMING THE DATAFRAME
    df = df[df['PercentGpA'] - df['PercentStd'] > 0]
    df = df[df['PercentStd'] < .5]

    # add energy differences to the dataframe
    cols = ['VDW', 'HBOND', 'IMM1']
    df = addEnergyDifferencesToDataframe(df, cols)

    # add interfaceSasa to the dataframe
    df['interfaceSasa'] = df['MonomerSasa'] - df['OptimizeSasa']
    df['vdwPerSasa'] = df['VDWDiff'] / df['interfaceSasa']
    df['hbondPerSasa'] = df['HBONDDiff'] / df['interfaceSasa']
    df['imm1PerSasa'] = df['IMM1Diff'] / df['interfaceSasa']
    df['totalPerSasa'] = df['Total'] / df['interfaceSasa']
    df.to_csv(f'{outputDir}/lowestEnergySequences.csv', index=False)

    # only plot the sequences with the HBONDDiff > 5
    lowHbond_df = df[df['HBONDDiff'] > -5]
    lowHbond_df = lowHbond_df[lowHbond_df[xAxis] < 0]
    # save the lowHbond_df to a csv file
    lowHbond_df.to_csv(f'{outputDir}/lowHbond_df.csv', index=False)
    # if df[xAxis] > 0, set the x-axis to be 0
    df.loc[df[xAxis] > 0, xAxis] = 0


    # save the df to a csv file
    df.to_csv(f'{outputDir}/plotData.csv', index=False)

    # make list of dfs to plot
    df_list = [df, lowHbond_df]
    outputTitle_list = ['TotalEnergy', 'LowHbond']
    if percentGpA_cutoff > 0:
        aboveCutoff_df = df[df['PercentGpA'] > percentGpA_cutoff]
        aboveCutoff_df.to_csv(f'{outputDir}/aboveCutoff_{percentGpA_cutoff*100}.csv', index=False)
        df_list.append(aboveCutoff_df)
        outputTitle_list.append('AboveCutoff')

    # make the directory for general outputs
    png_dir = f'{outputDir}/png'
    svg_dir = f'{outputDir}/svg'
    os.makedirs(png_dir, exist_ok=True)
    os.makedirs(svg_dir, exist_ok=True)
    for df_tmp,title in zip(df_list, outputTitle_list):
        plotScatterplot(df_tmp, xAxis, yAxis, yStd, regression_degree, title, png_dir, svg_dir)

    # make the directory for each sample
    for sample in df['Sample'].unique():
        sample_dir = f'{outputDir}/{sample}'
        png_dir = f'{sample_dir}/png'
        svg_dir = f'{sample_dir}/svg'
        os.makedirs(png_dir, exist_ok=True)
        os.makedirs(svg_dir, exist_ok=True)

    # plot the scatterplots for each sample
    for sample in df['Sample'].unique():
        df_sample = df[df['Sample'] == sample]
        # check that the df_sample is not empty
        if df_sample.empty:
            continue
        sample_dir = f'{outputDir}/{sample}'
        png_dir = f'{sample_dir}/png'
        svg_dir = f'{sample_dir}/svg'
        plotScatterplot(df_sample, xAxis, yAxis, yStd, regression_degree, f'{sample}_Total', png_dir, svg_dir)
        plotScatterplot(df_sample, xAxis, 'PercentGpA', 'PercentStd', regression_degree, f'{sample}_Total', png_dir, svg_dir)

    # plot individual scatterplots for each sample
    for sample, i in zip(df['Sample'].unique(), range(len(df['Sample'].unique()))):
        sample_dir = f'{outputDir}/{sample}'
        png_dir = f'{sample_dir}/png'
        svg_dir = f'{sample_dir}/svg'
        plotScatterplotSingle(df, sample, xAxis, yAxis, yStd, regression_degree, f'{sample}_Total', png_dir, svg_dir, sampleType=sample, color=colors[i])
        plotScatterplotSingle(df, sample, xAxis, 'PercentGpA', 'PercentStd', regression_degree, f'{sample}_Total', png_dir, svg_dir, sampleType=sample, color=colors[i])
    
    # define the energy diff / interfaceSasa
    df_all = df[(df['interfaceSasa'] > 0) & (df['vdwPerSasa'] < 0)]
    df_aboveCutoff = df_all[df_all['PercentGpA'] > percentGpA_cutoff]
    df_list = [df_all, df_aboveCutoff]
    output_list = ['all', 'aboveCutoff']
    for df_tmp,title in zip(df_list, output_list):
        for sample, i in zip(df_tmp['Sample'].unique(), range(len(df_tmp['Sample'].unique()))):
            sample_dir = f'{outputDir}/{sample}'
            png_dir = f'{sample_dir}/png'
            svg_dir = f'{sample_dir}/svg'
            plotScatterplotSingle(df_tmp, sample, 'interfaceSasa', yAxis, yStd, regression_degree, f'interfaceSasa_{title}', png_dir, svg_dir, sampleType=sample, color=colors[i], xlowLim=0, xhighLim=2000)
            plotScatterplotSingle(df_tmp, sample, 'vdwPerSasa', yAxis, yStd, regression_degree, f'vdwPerSasa_{title}', png_dir, svg_dir, sampleType=sample, color=colors[i], xlowLim=-.1, xhighLim=0)
            plotScatterplotSingle(df_tmp, sample, 'hbondPerSasa', yAxis, yStd, regression_degree, f'hbondPerSasa_{title}', png_dir, svg_dir, sampleType=sample, color=colors[i], xlowLim=-.05, xhighLim=.05)
            plotScatterplotSingle(df_tmp, sample, 'imm1PerSasa', yAxis, yStd, regression_degree, f'imm1PerSasa_{title}', png_dir, svg_dir, sampleType=sample, color=colors[i], xlowLim=0, xhighLim=.1)
            plotScatterplotSingle(df_tmp, sample, 'totalPerSasa', yAxis, yStd, regression_degree, f'totalPerSasa_{title}', png_dir, svg_dir, sampleType=sample, color=colors[i], xlowLim=-.1, xhighLim=0)