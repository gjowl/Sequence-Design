import os, sys, pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns

_sentinel = object()
def plotBoxplot(input_df, xaxis, yaxis, output_dir, output_filename=f"boxplot", xlabel=_sentinel, ylabel=_sentinel, ybottom=0, ytop=1.6):
    xlabel = xaxis if xlabel is _sentinel else xlabel
    ylabel = yaxis if ylabel is _sentinel else ylabel
    output_filename = f"{output_filename}_{xaxis}_vs_{yaxis}"
    # sort by the xaxis
    input_df = input_df.sort_values(by=[xaxis])
    sns.set_style("whitegrid")
    sns.boxplot(x=xaxis, y=yaxis,data=input_df, color='green', fliersize=2)
    sns.swarmplot(x=xaxis, y=yaxis, data=input_df, color='0', dodge=True, size=2)
    #calculate_pvalues(input_df)
    for i, sample in enumerate(input_df[xaxis].unique()):
        plt.text(i, 1.65, len(input_df[input_df[xaxis] == sample]), ha='left')
    # remove the legend
    plt.legend([],[], frameon=False)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    # set the y axis limits
    # get the lowest and highest values for y axis
    plt.ylim(bottom=ybottom)
    plt.ylim(top=ytop)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/{output_filename}.png')
    plt.clf()

# plots a boxplot for data that can be divided into multiple groups by a single columng
def plotMultiBoxplot(input_df, xaxis, yaxis, group_col, output_dir, output_filename=f"boxplot", xlabel=_sentinel, ylabel=_sentinel, ybottom=0, ytop=1.6):
    xlabel = xaxis if xlabel is _sentinel else xlabel
    ylabel = yaxis if ylabel is _sentinel else ylabel
    output_filename = f"{output_filename}_{xaxis}_vs_{yaxis}"
    # sort by the xaxis
    input_df = input_df.sort_values(by=[xaxis])
    sns.set_style("whitegrid")
    sns.boxplot(x=xaxis, y=yaxis, hue=group_col, data=input_df, color='green', fliersize=2)
    sns.swarmplot(x=xaxis, y=yaxis, hue=group_col, data=input_df, color='0', dodge=True, size=2)
    #calculate_pvalues(input_df)
    for i, sample in enumerate(input_df[xaxis].unique()):
        # separate the dataframe by mutant and wt
        # divide the size of the groups column by the number of groups
        groups = len(input_df[group_col].unique())
        dividers = [-.15, .15]  
        for divider, group in zip(dividers, input_df[group_col].unique()):
            df_group = input_df[input_df[group_col] == group]
            plt.text(i+divider, 1.65, len(df_group[df_group[xaxis] == sample]))
    # remove the swarm plot from the legend
    handles, labels = plt.gca().get_legend_handles_labels()
    plt.legend(handles[0:groups], labels[0:groups], frameon=False)
    #plt.legend([],[], frameon=False)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    # set the y axis limits
    # get the lowest and highest values for y axis
    plt.ylim(bottom=ybottom)
    plt.ylim(top=ytop)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/{output_filename}.png')
    plt.clf()
