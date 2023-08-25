import os, sys, pandas as pd, numpy as np, matplotlib.pyplot as plt

def getNumbersPerSample(input_dir):
    output_df = pd.DataFrame()
    for file in os.listdir(input_dir):
        # check if file contains mix
        if '21' in file:
            continue
        input_file = os.path.join(input_dir, file)
        # get the file name
        sample = file.split('.')[0]
        tmp = sample[:-2]
        print(sample)
        # read in the input file as a txt file after line 4
        df = pd.read_csv(input_file, sep='\t', skiprows=4)
        print(1)
        # only keep first 4 columns
        df = df.iloc[:, :4]
        print(2)
        header = ['Sequence', 'Count', 'Frequency', 'Segment']
        # set the header
        df.columns = header
        # keep only the segments that are not "Unknown"
        df = df[df['Segment'] != 'Unknown']
        # add the sample name as a row to the dataframe
        output_df = pd.concat([output_df, pd.DataFrame({'Sample': tmp, 'Filename': sample, 'Number': len(df)}, index=[0])], axis=0)
    return output_df

# read in the command line arguments
input_dir = sys.argv[1]
output_dir = sys.argv[2]

# make the output directory
os.makedirs(output_dir, exist_ok=True)

# loop through the input directory
df = getNumbersPerSample(input_dir)
df.to_csv(f'{output_dir}/segmentCounts.csv', index=False)

# loop through the samples
output_df = pd.DataFrame()
for sample in df['Sample'].unique():
    df_sample = df[df['Sample'] == sample].copy()
    # get the standard deviation
    std = df_sample['Number'].std()
    df_sample['std'] = std
    df_sample['std_percent'] = std/df_sample['Number']
    output_df = pd.concat([output_df, df_sample], axis=0)
output_df.to_csv(f'{output_dir}/segmentCounts_std.csv', index=False)
