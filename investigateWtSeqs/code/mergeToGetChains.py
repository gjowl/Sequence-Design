import os, sys, pandas as pd

# read in the command line arguments
allData_file = sys.argv[1]
finalData_file = sys.argv[2]

# read in the dataframes
allData_df = pd.read_csv(allData_file, sep='\t')
finalData_df = pd.read_csv(finalData_file, sep=',')

print(finalData_df)
# merge the Seg 1 Pos start Id into the finalData_df on sequence and pdb id without adding new rows
output_df = pd.merge(finalData_df, allData_df[['Seg 1 Pos start Id', 'Seg 2 Pos start Id', 'PDB Id', 'Sequence 1', 'Sequence 2']], on=['PDB Id', 'Sequence 1', 'Sequence 2'], how='left')
# keep the first occurrence of the pdb id and sequence
output_df = output_df.drop_duplicates(subset=['PDB Id', 'Sequence 1', 'Sequence 2'], keep='first')
# keep the first character of the Seg 1 Pos start Id
output_df['Chain 1'] = output_df['Seg 1 Pos start Id'].str[0]
output_df['Chain 2'] = output_df['Seg 2 Pos start Id'].str[0]
# remove the Seg 1 Pos start Id and Seg 2 Pos start Id columns
output_df = output_df.drop(columns=['Seg 1 Pos start Id', 'Seg 2 Pos start Id'])
print(output_df)
# write the output to a csv file
output_df.to_csv('finalDataWithChains.csv', index=False)