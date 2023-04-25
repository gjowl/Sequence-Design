import os, sys, pandas as pd

# read the command line arguments
input_file = sys.argv[1]
pdb_id_file = sys.argv[2]
output_file = sys.argv[3]

# read the input file
df = pd.read_csv(input_file, sep=',')
df_pdb_id = pd.read_csv(pdb_id_file, sep=',')

# combine the Position column for each sequence
df['Position'] = df['Position'].astype(str)
df['Position'] = df.groupby(['Sequence'])['Position'].transform(lambda x: ','.join(x))

# merge the df with the pdb id df; rid of sequences that are not in the pdb id df
df = pd.merge(df, df_pdb_id, on='Sequence', how='inner')

# keep the columns we want in order
df = df[['Sequence', 'pdbFileName', 'Position']]

# keep only the first sequence for each sequence
df = df.drop_duplicates(subset=['Sequence'], keep='first')

# output the data frame
df.to_csv(output_file, sep=',', index=False)