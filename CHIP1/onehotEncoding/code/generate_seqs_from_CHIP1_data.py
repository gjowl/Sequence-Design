import os, sys, pandas as pd

if __name__ == '__main__':
    # read in the command line arguments
    input_file = sys.argv[1]
    output_dir = sys.argv[2]

    # make the output directory if it doesn't exist
    os.makedirs(name=output_dir, exist_ok=True)

    # read in the input file as a dataframe
    df = pd.read_csv(input_file)

    # initialize the output dataframe
    output_df = pd.DataFrame()

    # keep any sequence combos that have 2 consecutive AAs that are L, separated by 2 AAs, or are only 2 AAs long
