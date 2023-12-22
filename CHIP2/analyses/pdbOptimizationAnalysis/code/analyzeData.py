import os, sys, pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np

colors = ['mediumseagreen', 'moccasin', 'darkslateblue', 'brown', 'pink', 'gray', 'olive', 'cyan']
# plot scatterplot function
#TODO: could get a standard deviation for the x axis energies now that I have multiple repack energies
def plotScatterplot(input_df, xAxis, yAxis, yStd, regression_degrees, output_title, png_dir, svg_dir, sampleType=0, color=0):
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
    plt.savefig(f'{png_dir}/scatter_{output_title}.png')
    plt.savefig(f'{svg_dir}/scatter_{output_title}.svg')
    # check if regression_degrees is a list
    for regression_degree in regression_degrees:
        # add a line of best fit and an r^2 value
        if regression_degree == 1:
            m, b = np.polyfit(input_df[xAxis], input_df[yAxis], regression_degree)
            plt.plot(input_df[xAxis], m*input_df[xAxis] + b, color='red')
            # add the r^2 value to the top left of the plot
            r2 = np.corrcoef(input_df[xAxis], input_df[yAxis])[0,1]**2
            plt.text(0.01, 1.10, f'r^2 = {r2:.2f}', transform=plt.gca().transAxes, fontsize=14, verticalalignment='top')
        if regression_degree == 2:
            m, b, c = np.polyfit(input_df[xAxis], input_df[yAxis], regression_degree)
            plt.plot(input_df[xAxis], c + b*input_df[xAxis] + m*input_df[xAxis]**2, color='red')
            # add the equation to the top left of the plot
            plt.text(0.01, 1.10, f'y = {m:.2f}x^2 + {b:.2f}x + {c:.2f}', transform=plt.gca().transAxes, fontsize=10, verticalalignment='top')
        if regression_degree == 3:
            m, b, c, d = np.polyfit(input_df[xAxis], input_df[yAxis], regression_degree)
            plt.plot(input_df[xAxis], d + c*input_df[xAxis] + b*input_df[xAxis]**2 + m*input_df[xAxis]**3, color='red')
            # add the equation to the top left of the plot
            plt.text(0.01, 1.10, f'y = {m:.2f}x^3 + {b:.2f}x^2 + {c:.2f}x + {d:.2f}', transform=plt.gca().transAxes, fontsize=10, verticalalignment='top')
        if regression_degree == 4:
            m, b, c, d, e = np.polyfit(input_df[xAxis], input_df[yAxis], regression_degree)
            plt.plot(input_df[xAxis], e + d*input_df[xAxis] + c*input_df[xAxis]**2 + b*input_df[xAxis]**3 + m*input_df[xAxis]**4, color='red')
            # add the equation to the top left of the plot
            plt.text(0.01, 1.10, f'y = {m:.2f}x^4 + {b:.2f}x^3 + {c:.2f}x^2 + {d:.2f}x + {e:.2f}', transform=plt.gca().transAxes, fontsize=10, verticalalignment='top')
        plt.savefig(f'{png_dir}/scatterRegression_{output_title}_{regression_degree}.png')
        plt.savefig(f'{svg_dir}/scatterRegression_{output_title}_{regression_degree}.svg')
        # remove the line of best fit
        plt.gca().lines.pop()
        # remove the r^2 value
        plt.gca().texts.pop()
    plt.close()
    plt.clf()

def plotScatterplotSingle(input_df, sample, xAxis, yAxis, yStd, regression_degrees, output_title, png_dir, svg_dir, sampleType=0, color=0, xlowLim=-60, xhighLim=0, ylowLim=0, yhighLim=1.75):
    df_sample = input_df[input_df['Sample'] == sample]
    # plot the WT sequence fluorescence vs the energy
    plt.scatter(df_sample[xAxis], df_sample[yAxis], color=colors[i], label=sample, s=5)
    # plot the standard deviation
    plt.errorbar(df_sample[xAxis], df_sample[yAxis], yerr=df_sample[yStd], fmt='o', color=colors[i], ecolor='dimgray', elinewidth=1, capsize=2, markersize=4)
    plt.text(0.99, 1.10, f'N = {len(input_df)}', transform=plt.gca().transAxes, fontsize=14, verticalalignment='top', horizontalalignment='right')
    plt.xlabel(xAxis)
    plt.ylabel(yAxis)
    # set the y axis limits
    plt.ylim(ylowLim, yhighLim)
    # set the x axis limits
    plt.xlim(xlowLim, xhighLim)
    plt.title(f'{xAxis} vs {yAxis}')
    plt.tight_layout()
    plt.savefig(f'{png_dir}/scatter_{output_title}.png')
    plt.savefig(f'{svg_dir}/scatter_{output_title}.svg')
    for regression_degree in regression_degrees:
        if regression_degree == 1:
            m, b = np.polyfit(input_df[xAxis], input_df[yAxis], regression_degree)
            plt.plot(input_df[xAxis], m*input_df[xAxis] + b, color='red')
            # add the r^2 value to the top left of the plot
            r2 = np.corrcoef(input_df[xAxis], input_df[yAxis])[0,1]**2
            plt.text(0.01, 1.10, f'r^2 = {r2:.2f}', transform=plt.gca().transAxes, fontsize=14, verticalalignment='top')
        if regression_degree == 2:
            m, b, c = np.polyfit(input_df[xAxis], input_df[yAxis], regression_degree)
            plt.plot(input_df[xAxis], c + b*input_df[xAxis] + m*input_df[xAxis]**2, color='red')
            # add the equation to the top left of the plot
            plt.text(0.01, 1.10, f'y = {m:.2f}x^2 + {b:.2f}x + {c:.2f}', transform=plt.gca().transAxes, fontsize=10, verticalalignment='top')
        if regression_degree == 3:
            m, b, c, d = np.polyfit(input_df[xAxis], input_df[yAxis], regression_degree)
            plt.plot(input_df[xAxis], d + c*input_df[xAxis] + b*input_df[xAxis]**2 + m*input_df[xAxis]**3, color='red')
            # add the equation to the top left of the plot
            plt.text(0.01, 1.10, f'y = {m:.2f}x^3 + {b:.2f}x^2 + {c:.2f}x + {d:.2f}', transform=plt.gca().transAxes, fontsize=10, verticalalignment='top')
        if regression_degree == 4:
            m, b, c, d, e = np.polyfit(input_df[xAxis], input_df[yAxis], regression_degree)
            plt.plot(input_df[xAxis], e + d*input_df[xAxis] + c*input_df[xAxis]**2 + b*input_df[xAxis]**3 + m*input_df[xAxis]**4, color='red')
            # add the equation to the top left of the plot
            plt.text(0.01, 1.10, f'y = {m:.2f}x^4 + {b:.2f}x^3 + {c:.2f}x^2 + {d:.2f}x + {e:.2f}', transform=plt.gca().transAxes, fontsize=10, verticalalignment='top')
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
        input_df[f'{col}Diff'] = input_df[f'{col}DimerOptimize'] - df[f'{col}Monomer']
    return input_df

if __name__ == '__main__':
    # read in the data file
    dataFile = sys.argv[1]
    df = pd.read_csv(dataFile)

    # get the output directory
    outputDir = sys.argv[2]

    # check if the percentGpA cutoff is provided
    if len(sys.argv) > 3:
        percentGpA_cutoff = float(sys.argv[3])
    else:
        percentGpA_cutoff = 0

    #xAxis = 'TotalPreOptimize'
    xAxis = 'Total'
    yAxis = 'PercentGpA'

    # make the output directory if it doesn't exist and the png and svg subdirectories
    os.makedirs(outputDir, exist_ok=True)

    # only keep sequences with the lowest total energy
    df = df.sort_values(by=[xAxis], ascending=True)
    df = df.drop_duplicates(subset=['Sequence'], keep='first')
    # move the sequence column to the front of the dataframe
    cols = df.columns.tolist()
    cols.insert(0, cols.pop(cols.index('Sequence')))

    # defining the regression degrees
    regression_degrees = [1, 2, 3, 4]

    # TRIMMING THE DATAFRAME
    df = df[df['PercentGpA'] < 2]
    df = df[df['PercentGpA'] - df['PercentStd'] > 0]
    df = df[df['PercentStd'] < .15]
    df = df[df['Sample'].notnull()]
    df = df[df['PercentGpA'] > 0]

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
    df = df[df[xAxis] < 0]

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
        plotScatterplot(df_tmp, xAxis, yAxis, 'PercentStd', regression_degrees, title, png_dir, svg_dir)

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
        plotScatterplot(df_sample, xAxis, yAxis, 'PercentStd', regression_degrees, f'{sample}_Total', png_dir, svg_dir)

    # plot individual scatterplots for each sample
    for sample, i in zip(df['Sample'].unique(), range(len(df['Sample'].unique()))):
        plotScatterplotSingle(df, sample, xAxis, yAxis, 'PercentStd', regression_degrees, f'{sample}_Total', png_dir, svg_dir, sampleType=sample, color=colors[i])
    
    # define the energy diff / interfaceSasa
    df_all = df[(df['interfaceSasa'] > 0) & (df['vdwPerSasa'] < 0)]
    df_aboveCutoff = df_all[df_all['PercentGpA'] > percentGpA_cutoff]
    df_list = [df_all, df_aboveCutoff]
    output_list = ['all', 'aboveCutoff']
    for df_tmp,title in zip(df_list, output_list):
        for sample, i in zip(df_tmp['Sample'].unique(), range(len(df_tmp['Sample'].unique()))):
            sample_dir = f'{outputDir}/{sample}'
            plotScatterplotSingle(df_tmp, sample, 'interfaceSasa', yAxis, 'PercentStd', regression_degrees, f'interfaceSasa_{title}', png_dir, svg_dir, sampleType=sample, color=colors[i], xlowLim=0, xhighLim=2000)
            plotScatterplotSingle(df_tmp, sample, 'vdwPerSasa', yAxis, 'PercentStd', regression_degrees, f'vdwPerSasa_{title}', png_dir, svg_dir, sampleType=sample, color=colors[i], xlowLim=-.1, xhighLim=0)
            plotScatterplotSingle(df_tmp, sample, 'hbondPerSasa', yAxis, 'PercentStd', regression_degrees, f'hbondPerSasa_{title}', png_dir, svg_dir, sampleType=sample, color=colors[i], xlowLim=-.05, xhighLim=.05)
            plotScatterplotSingle(df_tmp, sample, 'imm1PerSasa', yAxis, 'PercentStd', regression_degrees, f'imm1PerSasa_{title}', png_dir, svg_dir, sampleType=sample, color=colors[i], xlowLim=0, xhighLim=.1)
            plotScatterplotSingle(df_tmp, sample, 'totalPerSasa', yAxis, 'PercentStd', regression_degrees, f'totalPerSasa_{title}', png_dir, svg_dir, sampleType=sample, color=colors[i], xlowLim=0, xhighLim=.1)