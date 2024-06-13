import pandas as pd, sys

# read in the first file from command line
file1 = pd.read_csv(sys.argv[1])
file2 = pd.read_csv(sys.argv[2])

# keep the lowest total score for each sequence
if 'Total' not in file1.columns:
    print('Total column not found in', sys.argv[1])
else:
    file1 = file1.sort_values('Total').drop_duplicates('Sequence')
if 'Total' not in file2.columns:
    print('Total column not found in', sys.argv[2])
else:
    file2 = file2.sort_values('Total').drop_duplicates('Sequence')

# keep only the matching sequences
matching = pd.merge(file1, file2, on='Sequence')
# only keep the columns in file1
matching = matching[[col for col in file1.columns if col in matching.columns]]
# create the filename
filename = f'{sys.argv[1].split("/")[-1].split(".")[0]}_{sys.argv[2].split("/")[-1].split(".")[0]}_matching'
matching.to_csv(f'{filename}.csv', index=False)