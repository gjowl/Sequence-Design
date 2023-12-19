import os, sys, pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns
from scipy.stats import ttest_ind

_sentinel = object()
def plotBoxplot(input_df, xaxis, yaxis, output_dir, output_filename=f"boxplot", xlabel=_sentinel, ylabel=_sentinel, ybottom=0, ytop=1.6):
    # check if the input dataframe is empty
    if input_df.empty:
        return
    xlabel = xaxis if xlabel is _sentinel else xlabel
    ylabel = yaxis if ylabel is _sentinel else ylabel
    output_filename = f"{output_filename}_{xaxis}_vs_{yaxis}"
    # sort by the xaxis
    input_df = input_df.sort_values(by=[xaxis])
    sns.set_style("whitegrid")
    sns.boxplot(x=xaxis, y=yaxis,data=input_df, color='green', fliersize=2)
    #sns.swarmplot(x=xaxis, y=yaxis, data=input_df, color='0', dodge=True, size=1)
    sns.stripplot(x=xaxis, y=yaxis, data=input_df, color='0', dodge=True, size=2)
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
    plt.savefig(f'{output_dir}/{output_filename}.svg')
    plt.clf()

# labeling the boxplot with p values
def label_diff(i,j,text,X,Y):
    x = (X[i]+X[j])/2
    y = 1.1*max(Y[i], Y[j])
    dx = abs(X[i]-X[j])
    props = {'connectionstyle':'bar','arrowstyle':'-',\
                 'shrinkA':20,'shrinkB':20,'linewidth':2}
    plt.annotate(text, xy=(X[i],y+7), zorder=10)
    plt.annotate('', xy=(X[i],y), xytext=(X[j],y), arrowprops=props)

# plots a boxplot for data that can be divided into multiple groups by a single columng
def plotMultiBoxplot(input_df, xaxis, yaxis, group_col, output_dir, output_filename=f"boxplot", xlabel=_sentinel, ylabel=_sentinel, ybottom=0, ytop=1.6, hue_order=None):
    # check if the input dataframe is empty
    if input_df.empty:
        return
    if hue_order is None:
        hue_order = input_df[group_col].unique()
    xlabel = xaxis if xlabel is _sentinel else xlabel
    ylabel = yaxis if ylabel is _sentinel else ylabel
    output_filename = f"{output_filename}_{xaxis}_vs_{yaxis}"
    # sort by the xaxis
    input_df = input_df.sort_values(by=[xaxis])
    sns.set_style("whitegrid")
    sns.boxplot(x=xaxis, y=yaxis, hue=group_col, hue_order=hue_order, data=input_df, color='green', fliersize=2)
    sns.stripplot(x=xaxis, y=yaxis, hue=group_col, hue_order=hue_order, data=input_df, color='0', dodge=True, size=2)
    # calculate the p-value between the groups
    p_values = pd.DataFrame(columns=['sample', 'group', 'p_value'])
    for group in input_df[group_col].unique():
        wt = input_df[(input_df[group_col] == 'WT')]
        if group == 'WT':
            continue
        mut = input_df[(input_df[group_col] == group)]
        for sample in input_df[xaxis].unique():
            wt_sample = wt[wt[xaxis] == sample]
            mut_sample = mut[mut[xaxis] == sample]
            # calculate the p-value
            p_value = ttest_ind(wt_sample[yaxis], mut_sample[yaxis])[1]
            p_values = pd.concat([p_values, pd.DataFrame([[sample, group, p_value]], columns=['sample', 'group', 'p_value'])])
            #print(f'p-value between WT and {group}: {p_value}')
    # save the p-values to a csv file
    p_value_dir = f'{output_dir}/p_values'
    os.makedirs(name=p_value_dir, exist_ok=True)
    p_values.to_csv(f'{p_value_dir}/{xaxis}_{yaxis}.csv', index=False)
    for i, sample in enumerate(input_df[xaxis].unique()):
        # separate the dataframe by mutant and wt
        # divide the size of the groups column by the number of groups (works on groups of size 1-3)
        groups = len(hue_order)
        if groups == 1:
            dividers = [0]
        elif groups == 2:
            dividers = [-.15, .15]  
        elif groups == 3:
            dividers = [-.25, 0, .25]
        for divider, group in zip(dividers, hue_order):
            df_group = input_df[input_df[group_col] == group]
            plt.text(i + divider, 1.65, len(df_group[df_group[xaxis] == sample]), ha='left')
            # get the height of the highest point on the boxplot
            height = df_group[df_group[xaxis] == sample][yaxis].max()
            # define the height for the p-value
            height = height + .05
            if group != 'WT':
                p_value = p_values[(p_values['sample'] == sample) & (p_values['group'] == group)]['p_value'].values[0]
                #print(group, sample, p_value)
                if p_value < .05 and p_value >= .005:
                    plt.text(i + divider, height, f'p<.05', ha='center', fontsize=8)
                elif p_value < .005:
                    plt.text(i + divider, height, f'p<.005', ha='center', fontsize=8)
                else:
                    plt.text(i + divider, height, f'p={round(p_value, 3)}', ha='center', fontsize=8)
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
    plt.savefig(f'{output_dir}/{output_filename}.svg')
    plt.clf()
