import os, sys, pandas as pd
from oneHotEncoding import *

if __name__ == "__main__":
    # get the command line arguments
    input_file = sys.argv[1]
    output_dir= sys.argv[2]

    # make the output directory if it doesn't exist
    os.makedirs(name=output_dir, exist_ok=True)

    # read in a dataframe from the command line
    df = pd.read_csv(input_file, dtype={'Interface': str})

    # loop through each sequence in the dataframe
    sequence_one_hot_list = []
    for index, row in df.iterrows():
        # get the sequence
        sequence = row['Sequence']
        # convert the sequence to one-hot encoding
        one_hot = convert_to_onehot(sequence)
        # add the one-hot encoding to the list
        sequence_one_hot_list.append(one_hot)
    
    # add the one-hot encoding to the dataframe
    df['OneHot'] = sequence_one_hot_list

    # get the length of the one-hot encoding
    one_hot_length = len(df['OneHot'][0])
    # loop through every single position in the one-hot encoding
    for i in range(one_hot_length):
        # get the number of unique amino acids at that position
        unique_one_hot = df['OneHot'].str[i].astype(str).unique()
        if (len(unique_one_hot) > 1):
            # loop through the unique one-hot encodings
            output_df = pd.DataFrame()
            for one_hot in unique_one_hot:
                # convert the one-hot encoding to the amino acid
                amino_acid = decode_one_hot(one_hot)
                # get the dataframe with the matching one-hot encoding
                df_single_one_hot = getMatchingOneHotDf(df, amino_acid, i, 'AA1')
                # loop through the rest of the positions in the one-hot encoding
                for j in range(i+1, one_hot_length):
                    # get the number of unique amino acids at that position
                    unique_one_hot_2 = df_single_one_hot['OneHot'].str[j].astype(str).unique()
                    if (len(unique_one_hot_2) > 1):
                        # loop through the unique one-hot encodings
                        for one_hot_2 in unique_one_hot_2:
                            # convert the one-hot encoding to the amino acid
                            amino_acid_2 = decode_one_hot(one_hot_2)
                            # get the dataframe with the matching one-hot encoding
                            df_double_one_hot = getMatchingOneHotDf(df_single_one_hot, amino_acid_2, j, 'AA2')
                            # add the position to the dataframe
                            df_double_one_hot['Position'] = f'{i}_{j}'
                            # remove the one-hot encoding from the dataframe
                            df_double_one_hot = df_double_one_hot.drop(columns=['OneHot', 'tmp'])
                            # make the amino acid directory if it doesn't exist
                            aa_dir = f'{output_dir}/{amino_acid}'
                            os.makedirs(name=aa_dir, exist_ok=True)
                            # save the data to a csv file
                            output_df.to_csv(f'{aa_dir}/{amino_acid}.csv', index=False)