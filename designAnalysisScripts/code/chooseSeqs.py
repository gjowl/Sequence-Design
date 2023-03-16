import os, sys, pandas as pd, numpy as np, matplotlib.pyplot as plt

"""
This script will read in a csv file and a number from the command line, comb through the geometric data, and output a csv file
with the number of sequences for each cluster that can be used for experiments.
"""

if __name__ == "__main__":
    # read in the data from command line
    data = sys.argv[1]
    outputDir = sys.argv[2]
    numSeqs = int(sys.argv[3])

    # make the output directory
    os.makedirs(name=outputDir, exist_ok=True)

    # read in the data
    df = pd.read_csv(data)

    # add the xChange and crossChange columns together
    df['geomChange'] = df['xChange'] + df['crossChange']

    # normalize the xChange and crossChange columns
    df['geomChangeNorm'] = (df['geomChange'] - df['geomChange'].min()) / (df['geomChange'].max() - df['geomChange'].min())

    cutoff_list = [0.2, 0.4, 0.6, 0.8, 1.0]
    
    # loop through the regions
    for region in df['Region'].unique():
        # initialize the output dataframe
        output_df = pd.DataFrame()
        # get the data for the region
        region_df = df[df['Region'] == region]
        # loop through the cutoffs
        for cutoff in cutoff_list:
            # initialize the cutoff dataframe
            cutoff_df = pd.DataFrame()
            # check if the cutoff is the first cutoff
            if cutoff == cutoff_list[0]:
            # get the data for the cutoff
                cutoff_df = region_df[region_df['geomChangeNorm'] <= cutoff]
            elif cutoff != cutoff_list[len(cutoff_list)-1]:
                cutoff_df = region_df[(region_df['geomChangeNorm'] > cutoff_list[cutoff_list.index(cutoff) - 1]) & (region_df['geomChangeNorm'] <= cutoff)]
            else:
                cutoff_df = region_df[region_df['geomChangeNorm'] > cutoff_list[cutoff_list.index(cutoff) - 1]]
            # randomly sample the cutoff dataframe
            num_seqs = int(numSeqs/len(cutoff_list))
            #TODO: fix this so that it outputs properly
            cutoff_df = cutoff_df.sample(n=num_seqs, random_state=1)
            # append the cutoff dataframe to the output dataframe using concat
            output_df = pd.concat(objs=[output_df, cutoff_df], axis=0)
        # output the data to a csv file
        output_df.to_csv(f'{outputDir}/{region}_seqs.csv', index=False)