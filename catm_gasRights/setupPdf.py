import os, sys, pandas as pd, numpy as np, argparse
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind

# initialize the parser
parser = argparse.ArgumentParser(description='Output the pdf table for averages of CATM data sequence')
parser.add_argument('-inputFile','--inputFile', type=str, help='the input averages csv file')
parser.add_argument('-outDir','--outputDir', type=str, help='the output directory')

# extract the arguments into variables
args = parser.parse_args()
# necessary arguments
inputFile = args.inputFile
# optional arguments
outputDir = os.getcwd()
if args.outputDir is not None:
    outputDir = args.outputDir
    os.makedirs(outputDir, exist_ok=True)

if __name__ == '__main__':
    # read in the data
    df = pd.read_csv(inputFile, sep=',')
    sig_figs = 2
    cols = ['Low', 'Medium', 'High', 'AboveGpA']

    # get the name of the first column
    first_col = df.columns[0]
    # combine the columns of value and stdev into one column, rounding to specified decimal places
    output_df = df.copy()
    for col in cols:
        output_df[col] = output_df[col].round(sig_figs).astype(str) + ' ± ' + output_df[f'{col}Std'].round(sig_figs).astype(str)
    
    # keep only the columns of interest and the first column
    cols = [first_col] + cols
    output_df = output_df[cols]
    output_df.to_csv(os.path.join(outputDir, 'averages_table.csv'), index=False)