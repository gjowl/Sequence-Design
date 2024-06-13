import pandas as pd, sys

# read in the first file from command line
file1 = pd.read_csv(sys.argv[1])
file2 = pd.read_csv(sys.argv[2])

# keep the lowest total score for each sequence
file1 = file1.sort_values('Total').drop_duplicates('Sequence')
file2 = file2.sort_values('Total').drop_duplicates('Sequence')

# keep only the matching sequences
matching = pd.merge(file1, file2, on='Sequence')
matching.to_csv('matching.csv', index=False)