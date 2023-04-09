import os, sys, pandas as pd

# get the command line arguments
input_dir = sys.argv[1]
input_csv = sys.argv[2]
output_dir = sys.argv[3]

# make the output directory if it doesn't exist
os.makedirs(name=output_dir, exist_ok=True)

# read in the csv file
df = pd.read_csv(input_csv, sep=',', header=0)

# keep the sequence, directory, and pdb file name
df = df[['Sequence', 'replicateNumber', 'Directory']]

# get the design number from the Directory column
df['designNumber'] = df['Directory'].str.split('_').str[1]

# make a new column for the pdb file name combining the directory and the replicate number
df['pdbFileName'] = df['designNumber'] + '_' + df['replicateNumber'].astype(str) + '.pdb'

# loop through all directories
for dir in df['Directory'].unique():
    # loop through all files in the directory
    filenames = df[df['Directory'] == dir]['pdbFileName']
    for file in os.listdir(input_dir + '/' + dir):
        # check if the file is in the dataframe
        if file in filenames.values:
            # copy the file to the output directory
            os.system(f'cp {input_dir}/{dir}/{file} {output_dir}/{file}')

# remove the directory and replicate number columns
df = df.drop(columns=['replicateNumber','Directory', 'designNumber'])

# save the dataframe to a csv file
df.to_csv(f'{output_dir}/pdbFiles.csv', index=False)
print('pdb files put in ', output_dir)