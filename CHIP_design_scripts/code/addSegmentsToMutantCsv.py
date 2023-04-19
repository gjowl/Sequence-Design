import os, sys, pandas as pd

"""
This script will take a wt sequence file and a mutant sequence file and add the segment information to the mutant sequence file.
Specifically for designs labeled with the region column and the segment column.
"""

# read in the command line arguments
wt_file = sys.argv[1]
mutant_file = sys.argv[2]

# get the mutant name from the mutant file without the file extension
mutant_filename = os.path.splitext(os.path.basename(mutant_file))[0]

# read in the input file as a dataframe
wt_df = pd.read_csv(wt_file)
mutant_df = pd.read_csv(mutant_file)

# loop through the regions
output_df = pd.DataFrame()
for region in wt_df['Region'].unique():
    # get the data for the region
    wt_region_df = wt_df[wt_df['Region'] == region]
    mutant_region_df = mutant_df[mutant_df['Region'] == region]
    # merge the dataframes on the Sequence column
    mutant_region_df = pd.merge(mutant_region_df, wt_region_df[['Sequence', 'Segment']], on='Sequence', how='right')
    # add the mutant_region_df to the output dataframe
    output_df = pd.concat([output_df, mutant_region_df], axis=0)

# sort by region and segment
output_df = output_df.sort_values(by=['Region', 'Segment'])
# add the size of the unique segments to the segment column
output_df['Segment'] = output_df['Segment'] + output_df['Segment'].nunique()
# save the output dataframe to a csv file
output_df.to_csv(f'{mutant_filename}_withSegments.csv', index=False)

# save the output dataframe to a csv file with only the columns we need
output_df[['Mutant','Region','Segment']].to_csv(f'{mutant_filename}_withSegments_simplified.csv', index=False)

