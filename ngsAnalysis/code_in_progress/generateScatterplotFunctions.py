import sys
from functions import *
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as cs
import random
import re
from sklearn.metrics import r2_score

def outputRegressionLine(x, y):
    # fit a line to a 1 degree polynomial
    model = np.polyfit(x, y, 1)
    # prediction for a line of best fit
    predict = np.poly1d(model)
    #calculate R-squared of regression model
    r2 = r2_score(y, predict(x))
    #obtain m (slope) and b(intercept) of linear regression line
    m, b = model[0], model[1]
    #add linear regression line to scatterplot 
    line = plt.plot(x, m*x+b, label='y={:.2f}x+{:.2f}\nR²={:.2g}'.format(m, b, r2), c='orange')
    return line, r2
    
def createScatterPlotDiffLabels(df, xAxis, yAxis, labelName, outFile, title):
    # setup figure and axes
    fig, ax = plt.subplots()
    # set axis title
    ax.set_title(title)
    # set axes labels
    ax.set_xlabel('Energy Score')
    ax.set_ylabel('Fluorescence')
    # get values from dataframe
    x = df[xAxis]
    y = df[yAxis]
    # values need to be in list format for scatterplot
    xList = x.tolist()
    yList = y.tolist()
    labels = df[labelName].tolist()
    # get a color map based on the length of the input
    colormap = cm.viridis
    colorlist = [cs.rgb2hex(colormap(i)) for i in np.linspace(0, 0.9, len(labels))]
    # loop through the dataframe to output the scatterplot with points in different colors 
    for i,c in enumerate(colorlist):
        x1=xList[i]
        y1=yList[i]
        l=labels[i]
        plt.scatter(x1, y1, label=l, s=50, linewidth=0.1, c=c)
    # TODO: fix so that there's a separate legend for regression
    # outputs a regression line and equation 
    l1 = outputRegressionLine(x, y)
    l2 = plt.legend(fontsize=6, loc='center right')
    #plt.gca().add_artist(l2)
    # save image to filename
    fig.savefig(outFile,format='png', dpi=1200)
    
def createScatterPlot(df, xAxis, yAxis, stdDev, r2Cutoff, filename, title):
    # setup figure and axes
    fig, ax = plt.subplots()
    # get values from dataframe
    x = df[xAxis]
    y = df[yAxis]
    if len(x) > 1:
        # outputs a regression line and equation 
        line, r2 = outputRegressionLine(x, y)
        if r2 >= r2Cutoff:
            print(title, r2)
            # set axis title
            ax.set_title(title)
            # set axes labels
            ax.set_xlabel('Energy Score')
            ax.set_ylabel('Fluorescence')
            stdDev = df[stdDev]
            # get the wild type value from the dataframe
            df_wt = df[df['StartSequence'] == df['Sequence']] 
            x_wt = df_wt[xAxis]
            y_wt = df_wt[yAxis]
            # values need to be in list format for scatterplot
            xList = x.tolist()
            yList = y.tolist()
            # plot scatter plot for mutants
            plt.errorbar(x, y, stdDev, linestyle='None', marker='', capsize=4, c='black')
            plt.scatter(x, y, s=50, linewidth=0.1)
            plt.scatter(x_wt, y_wt, s=50, linewidth=0.1, c='r')
            # TODO: fix so that there's a separate legend for regression
            l2 = plt.legend(fontsize=6, loc='upper right')
            #plt.gca().add_artist(l2)
            # save image to filename
            fig.savefig(filename+'.png',format='png', dpi=1200)
            df.to_csv(filename+'.csv', index=False)
    plt.close()

def getScatterplotsForDfList(list_df, nameCol, xAxis, yAxis, stdDev, r2Cutoff, outputDir):
    # iterate through the list of dataframes
    for df in list_df:
        df.loc[df[xAxis] > 0, xAxis] = 0
        # sorts the df by Total energy score
        df = df.sort_values(by=xAxis)
        df = df.reset_index(drop=True)
        # get the name value for the filename
        name = df[nameCol][0]
        graphTitle = str(name)
        filename = outputDir+graphTitle
        # create the scatter plot
        createScatterPlot(df,xAxis,yAxis,stdDev,r2Cutoff,filename,graphTitle)

def getListOfDfWithUniqueColumnVal(df, colName):
    list_df = []
    for num in df[colName].unique():
        out_df = df[df[colName] == num]
        list_df.append(out_df)
    return list_df
