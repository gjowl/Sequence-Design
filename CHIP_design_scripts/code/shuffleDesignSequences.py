import os, sys, pandas as pd

# read in the command line arguments
input_file = sys.argv[1]
num_splits = int(sys.argv[2])
output_dir = sys.argv[3]

# get the input filename without the extension
input_filename = os.path.splitext(os.path.basename(input_file))[0]

# make the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# read in the input file as a dataframe
df = pd.read_csv(input_file)

# loop through the regions
output_df = pd.DataFrame()
for region in df['Region'].unique():
    # get the data for the region
    region_df = df[df['Region'] == region]
    # get the length of the dataframe
    num_mutants = len(region_df)
    # loop through the number of splits
    # split the dataframe into  equal parts, shuffled
    region_df = region_df.sample(frac=1).reset_index(drop=True)
    for i in range(num_splits):
        # get the i th split
        region_df_i = region_df.iloc[i*num_mutants//num_splits:(i+1)*num_mutants//num_splits]
        # add a segment number column without copy warning
        region_df_i = region_df_i.assign(Segment=i)
        # add the half dataframes to the output dataframe
        output_df = pd.concat([output_df, region_df_i], axis=0)

# save the output dataframe to a csv file
output_df.to_csv(f'{output_dir}/{input_filename}_shuffled.csv', index=False)


