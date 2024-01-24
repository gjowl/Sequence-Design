import os, sys, pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns, argparse
from boxplotFunctions import plotBoxplot, plotMultiBoxplot

# initialize the parser
parser = argparse.ArgumentParser(description='Graph the change in fluorescence for each sequence-mutant pair')

# add the necessary arguments
parser.add_argument('-inFile','--inputFile', type=str, help='the input csv file')
# add the optional arguments
parser.add_argument('-outDir','--outputDir', type=str, help='the output directory')

# extract the arguments into variables
args = parser.parse_args()
sequenceFile = args.inputFile
# default values for the optional arguments
outputDir = os.getcwd() 
# if the optional arguments are not specified, use the default values
if args.outputDir is not None:
    outputDir = args.outputDir
    os.makedirs(outputDir, exist_ok=True)

if __name__ == '__main__':
    # read in the input files
    df_seq = pd.read_csv(sequenceFile) 
    
    # make the output directory
    os.makedirs(outputDir, exist_ok=True)
    
    yaxis = 'Delta Fluorescence'
    xaxis = 'Sample'
    
    # plot the boxplots
    filename = os.path.basename(sequenceFile).split('.')[0]
    
    df_seq.sort_values(by='Type', inplace=True)
    for sample in df_seq['Sample'].unique():
        df_sample = df_seq[df_seq['Sample'] == sample]
        sample_outputDir = f'{outputDir}/{sample}'
        os.makedirs(sample_outputDir, exist_ok=True)
        df_sample.sort_values(by='Mutant Type')
        plotMultiBoxplot(df_sample, xaxis, yaxis, 'Mutant Type', sample_outputDir, ybottom=-1, ytop=1)