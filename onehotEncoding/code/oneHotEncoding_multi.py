import os, sys, pandas as pd
from oneHotEncoding import *

def getNextOneHotDf(df, amino_acid, prior_pos, one_hot_length, column_name):
    # initialize the output dataframe
    output_df = pd.DataFrame()
    # loop through the rest of the positions in the one-hot encoding
    for j in range(prior_pos+1, one_hot_length):
        # get the number of unique amino acids at that position
        unique_one_hot = df['OneHot'].str[j].astype(str).unique()
        if (len(unique_one_hot) > 1):
            # loop through the unique one-hot encodings
            for one_hot in unique_one_hot:
                # convert the one-hot encoding to the amino acid
                amino_acid = decode_one_hot(one_hot)
                # get the dataframe with the matching one-hot encoding
                df_one_hot = getMatchingOneHotDf(df, amino_acid, j, column_name)
                # append the current position to the dataframe
                df_one_hot['Position'] = [f'{pos}_{j}' for pos in df_one_hot['Position']]
                # add the dataframe to the output dataframe using concat
                output_df = pd.concat([output_df, df_one_hot])
    return output_df

if __name__ == "__main__":
    # get the command line arguments
    input_file = sys.argv[1]
    output_dir= sys.argv[2]
    aa_number = int(sys.argv[3])

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
            for one_hot in unique_one_hot:
                output_df = pd.DataFrame()
                # convert the one-hot encoding to the amino acid
                amino_acid = decode_one_hot(one_hot)
                # make the amino acid directory if it doesn't exist
                aa_dir = f'{output_dir}/{amino_acid}'
                os.makedirs(name=aa_dir, exist_ok=True)
                # get the dataframe with the matching one-hot encoding
                df_single_one_hot = getMatchingOneHotDf(df, amino_acid, i, f'AA{i}')
                # add the position to the dataframe
                df_single_one_hot['Position'] = f'{i}'
                df_one_hot = df_single_one_hot.copy()
                for j in range(aa_number):
                    df_one_hot = getNextOneHotDf(df_one_hot, amino_acid, i, one_hot_length, f'AA{i+j+1}') 
                # remove the one-hot encoding from the dataframe
                df_one_hot = df_one_hot.drop(columns=['OneHot', 'tmp'])
                output_df = pd.concat([output_df, df_one_hot])
                # check if output_df is empty
                if (output_df.empty):
                    continue
                # save the data to a csv file
                output_df.to_csv(f'{aa_dir}/{amino_acid}_{i}.csv', index=False)
                exit(0)