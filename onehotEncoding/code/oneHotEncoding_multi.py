import os, sys, pandas as pd
from oneHotEncoding import *

def getNextOneHotDf(df, amino_acid, unique_indices, current_pos, column_name):
    # initialize the output dataframe
    output_df = pd.DataFrame()
    for position in df['Position'].unique():
        # get the dataframe with the matching position
        df_position = df[df['Position'] == position]
        # check if position is a string
        if (isinstance(position, str)):
            # get the final part of the string separated by '_'
            current_pos = int(position.split('_')[-1])
        # get the one-hot encoding
        for i in unique_indices:
            if (i > current_pos):
                print(f'Position: {current_pos}, Index: {i}')
                unique_one_hot = df_position['OneHot'].str[i].astype(str).unique()
                # loop through the unique one-hot encodings
                for one_hot in unique_one_hot:
                    # convert the one-hot encoding to the amino acid
                    amino_acid = decode_one_hot(one_hot)
                    # get the dataframe with the matching one-hot encoding
                    df_one_hot = getMatchingOneHotDf(df_position, amino_acid, i, column_name)
                    # append the current position to the dataframe
                    df_one_hot['Position'] = [f'{pos}_{i}' for pos in df_one_hot['Position']]
                    # add the dataframe to the output dataframe using concat
                    output_df = pd.concat([output_df, df_one_hot])
    return output_df


def getUniqueOneHotIndex(df):
    one_hot_indices = []
    # reset the index of the dataframe; indices change when the dataframe is sliced
    df = df.reset_index(drop=True)
    for i in range(len(df['OneHot'][0])):
        unique_one_hot = df['OneHot'].str[i].astype(str).unique()
        if (len(unique_one_hot) > 1):
            one_hot_indices.append(i)
    return one_hot_indices

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

    one_hot_indices = getUniqueOneHotIndex(df)
    for i in one_hot_indices:
        # get the number of unique amino acids at that position
        unique_one_hot = df['OneHot'].str[i].astype(str).unique()
        # loop through the unique one-hot encodings
        for one_hot in unique_one_hot:
            output_df = pd.DataFrame()
            # convert the one-hot encoding to the amino acid
            amino_acid = decode_one_hot(one_hot)
            # make the amino acid directory if it doesn't exist
            aa_dir = f'{output_dir}/{amino_acid}_{i}'
            os.makedirs(name=aa_dir, exist_ok=True)
            # get the dataframe with the matching one-hot encoding
            df_single_one_hot = getMatchingOneHotDf(df, amino_acid, i, f'AA{i}')
            # add the position to the dataframe
            df_single_one_hot['Position'] = i
            df_one_hot = df_single_one_hot.copy()
            current_pos = i
            for j in range(aa_number):
                # get the next one-hot encoding index
                unique_indices = getUniqueOneHotIndex(df_one_hot)
                # get the next one-hot encoding dataframe
                df_one_hot = getNextOneHotDf(df_one_hot, amino_acid, unique_indices, current_pos, f'AA{i+j+1}')
            # remove the one-hot encoding from the dataframe
            df_one_hot = df_one_hot.drop(columns=['OneHot', 'tmp'])
            # split the position column by the underscore
            output_df = pd.concat([output_df, df_one_hot])
            # check if output_df is empty
            if (output_df.empty):
                continue
            # separate the dataframes by unique positions
            for position in output_df['Position'].unique():
                pos_df = output_df[output_df['Position'] == position]
                # save the data to a csv file
                pos_df.to_csv(f'{aa_dir}/{amino_acid}_{position}.csv', index=False)
            exit(0)