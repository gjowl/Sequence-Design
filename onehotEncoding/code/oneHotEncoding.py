import os, sys, pandas as pd

# alphabet of all possible chars you want to convert
alphabet = "ACDEFGHIKLMNPQRSTVWY"

def convert_to_onehot(data):
    # Creates a dict, that maps to every char of alphabet an unique int based on position
    char_to_int = dict((c,i) for i,c in enumerate(alphabet))
    encoded_data = []
    # Replaces every char in data with the mapped int
    encoded_data.append([char_to_int[char] for char in data])
    #print(encoded_data) # Prints the int encoded array

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

def convert_onehot_to_AA(one_hot):
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

    sequence_length = len(df['Sequence'][0])
    # get the ith position of the one-hot encoding
    # create a dataframe with the amino acid, position, and the fluorescence
    df_amino_acid = pd.DataFrame(columns=['AminoAcid', 'Position', 'Total'])
    tester = df["OneHot"][0][3]
    test = str(tester)
    print(test)
    print(convert_onehot_to_AA(tester))
    # convert the one-hot encoding to the amino acid
    test_aa = convert_onehot_to_AA(tester)

    #output_df['crossingAngle'] = output_df['crossingAngle'].apply(lambda x: x*-1 if x > 0 else x)
    #for onehot in df["OneHot"].str[0]:
    #    print(convert_onehot_to_AA(onehot))# TODO: clean this up; it works now, but it's not pretty
    print(df["OneHot"].str[0].astype(str))
    df['tmp'] = df["OneHot"].str[3].astype(str)
    print(df['tmp'][3])
    df['tmp'] = df['tmp'].apply(convert_onehot_to_AA)
    #df_test = df[df["OneHot"].str[0].astype(str).str.contains(test)]
    df_test = df[df["tmp"].str.contains(test_aa)]
    print(df_test)
    df_test.to_csv(f'{output_dir}/amino_acid_fluorescence.csv', index=False)

    # get the length of the one-hot encoding
    one_hot_length = len(df['OneHot'][0])
    # loop through every single position in the one-hot encoding
    for i in range(one_hot_length):
        # get the number of unique amino acids at that position
        unique_one_hot = df['OneHot'].str[i].astype(str).unique()
        if (len(unique_one_hot) > 1):
            # loop through the unique one-hot encodings
            for one_hot in unique_one_hot:
                # initialize a dataframe for output
                output_df = df.copy()
                # convert the one-hot encoding to the amino acid
                amino_acid = convert_onehot_to_AA(one_hot)
                # add the one-hot encoding for the position to a tmp column in the dataframe
                output_df['tmp'] = output_df["OneHot"].str[i].astype(str)
                # convert the one-hot encoding to the amino acid
                output_df['tmp'] = output_df['tmp'].apply(convert_onehot_to_AA)
                # keep only the data with matching amino acids at that position
                output_df = output_df[output_df['tmp'].str.contains(amino_acid)]
                # make the amino acid directory if it doesn't exist
                aa_dir = f'{output_dir}/{amino_acid}'
                os.makedirs(name=aa_dir, exist_ok=True)
                # save the data to a csv file
                output_df.to_csv(f'{aa_dir}/{amino_acid}_{i}.csv', index=False)
    exit(0)

    # Now I want to search for the amino acid at each position and correlate that to fluorescence
    """
    Could I do the following:
        - Get a dataframe of all amino acids at each position, take the fluorescence of each amino acid, average it and show it as a boxplot for each position
    """

    # 