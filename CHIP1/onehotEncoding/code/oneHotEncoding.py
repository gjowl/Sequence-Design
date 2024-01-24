import os, sys, pandas as pd

# alphabet of all possible chars you want to convert
alphabet = "ACDEFGHIKLMNPQRSTVWY"

def add_onehot_to_df(df):
    # initialize a list to hold the one-hot encoding
    sequence_one_hot_list = []
    # loop through each sequence in the dataframe
    for index, row in df.iterrows():
        # get the sequence
        sequence = row['Sequence']
        # convert the sequence to one-hot encoding
        one_hot = convert_to_onehot(sequence)
        # add the one-hot encoding to the list
        sequence_one_hot_list.append(one_hot)
    # add the one-hot encoding to the dataframe
    df['OneHot'] = sequence_one_hot_list
    return df

def convert_to_onehot(data):
    # Creates a dict, that maps to every char of alphabet an unique int based on position
    char_to_int = dict((c,i) for i,c in enumerate(alphabet))
    encoded_data = []
    # Replaces every char in data with the mapped int
    encoded_data.append([char_to_int[char] for char in data])
    # This part now replaces the int by an one-hot array with size alphabet
    one_hot = []
    for value in encoded_data:
        for i in value:
            # At first, the whole array is initialized with 0
            letter = [0 for _ in range(len(alphabet))]
            # if value is the index of the letter, it is set to 1
            letter[i] = 1
            one_hot.append(letter)
    return one_hot

def decode_one_hot(one_hot):
    # check if the one-hot encoding is a list
    if type(one_hot) == str:
        # convert the string to a list of ints ridding of the brackets
        one_hot = one_hot[1:-1].split(', ')
        one_hot = [int(i) for i in one_hot]
    # get the index where the one-hot encoding is 1
    index = one_hot.index(1)
    # get the amino acid at the index
    amino_acid = alphabet[index]
    return amino_acid

def getMatchingOneHotDf(df, decoded_one_hot, position, col_name):
    # initialize a dataframe for output
    output_df = df.copy()
    # add the one-hot encoding for the position to a tmp column in the dataframe
    output_df['tmp'] = output_df["OneHot"].str[position].astype(str)
    # convert the one-hot encoding to the amino acid
    output_df[col_name] = output_df['tmp'].apply(decode_one_hot)
    # keep only the data with matching amino acids at that position
    output_df = output_df[output_df[col_name].str.contains(decoded_one_hot)]
    return output_df

if __name__ == "__main__":
    # get the command line arguments
    input_file = sys.argv[1]
    output_dir= sys.argv[2]

    # make the output directory if it doesn't exist
    os.makedirs(name=output_dir, exist_ok=True)

    # read in a dataframe from the command line
    df = pd.read_csv(input_file, dtype={'Interface': str})

    # add the one-hot encoding to the dataframe
    df = add_onehot_to_df(df)

    # get the length of the one-hot encoding
    one_hot_length = len(df['OneHot'][0])

    # loop through every single position in the one-hot encoding
    for i in range(one_hot_length):
        # get the number of unique one hot encodings at that position
        unique_one_hot = df['OneHot'].str[i].astype(str).unique()
        if (len(unique_one_hot) > 1):
            # loop through the unique one-hot encodings
            for one_hot in unique_one_hot:
                # convert the one-hot encoding to the amino acid
                amino_acid = decode_one_hot(one_hot)
                # get the dataframe with the matching one-hot encoding
                output_df = getMatchingOneHotDf(df, amino_acid, i, 'AA')
                # add the position to the dataframe
                output_df['Position'] = i 
                # remove the one-hot encoding from the dataframe
                output_df = output_df.drop(columns=['OneHot', 'tmp'])
                # make the amino acid directory if it doesn't exist
                aa_dir = f'{output_dir}/{amino_acid}'
                os.makedirs(name=aa_dir, exist_ok=True)
                # save the data to a csv file
                output_df.to_csv(f'{aa_dir}/{amino_acid}_{i}.csv', index=False)