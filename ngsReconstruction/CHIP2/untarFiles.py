

"""
Untar a list of files in a given directory
"""

import os, sys
import gzip, shutil

# read in the directory from command line
input_dir = sys.argv[1]
output_dir = sys.argv[2]

# make the output directory if it doesn't exist
os.makedirs(name=output_dir, exist_ok=True)

# get all files in the directory
files = os.listdir(input_dir)

# loop through all files in the directory
for file in files:
    # unzip the file
    with gzip.open(input_dir+file, 'rb') as f_in:
        with open(output_dir+file[:-3], 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
            print(f_out)