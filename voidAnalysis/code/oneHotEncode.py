import os, sys, pandas as pd

# alphabet of all possible chars you want to convert
alphabet = "ACDEFGHIKLMNPQRSTVWY"

def add_onehot_to_df(df, col_name):
    # initialize a list to hold the one-hot encoding
    sequence_one_hot_list = []
    # loop through each sequence in the dataframe
    for index, row in df.iterrows():
        # get the sequence
        sequence = row[col_name]
        # convert the sequence to one-hot encoding
        one_hot = convert_to_onehot(sequence)
        # add the one-hot encoding to the list
        sequence_one_hot_list.append(one_hot)
    # add the one-hot encoding to the dataframe
    df[f'{col_name}_OneHot'] = sequence_one_hot_list
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
    output_file = sys.argv[2]
    output_dir= sys.argv[3]
    columns = sys.argv[4:]

    # check if dataFile exists
    if os.path.isfile(f'{output_dir}/{output_file}'):
        # quit
        print('DataFile', output_file,'exists. To overwrite, delete the file and run again.')
        sys.exit()
    # get the input file name without the extension
    input_file_name = os.path.splitext(os.path.basename(input_file))[0]

    # make the output directory if it doesn't exist
    os.makedirs(name=output_dir, exist_ok=True)

    # read in a dataframe from the command line
    df = pd.read_csv(input_file, dtype={'Interface': str})

    # remove any sequences that don't have matching first 3 and last 3 residues between Sequence and Mutant
    df = df[df['Sequence'].str[:3] == df['Mutant'].str[:3]]
    df = df[df['Sequence'].str[-4:] == df['Mutant'].str[-4:]]

    for col in columns:
        # add the one-hot encoding to the dataframe
        df = add_onehot_to_df(df, col)
    
    output_df = pd.DataFrame()
    # output the dataframe to a csv file
    for seq in df['Sequence'].unique():
        # get the data for the sequence
        seq_df = df[df['Sequence'] == seq]
        # get the list of positions that are 0 in the interface
        interface_positions = [i for i, x in enumerate(seq_df['Interface'].values[0]) if x == '0']
        # rid of the ones in the list that are before 3 or after 18
        interface_positions = [i for i in interface_positions if i > 2 and i < 19]
        # loop through the mutants
        mutant_df = pd.DataFrame()
        for mutant in seq_df['Mutant']:
            # loop through the interface positions
            keep_mutant = True
            for interface in interface_positions:
                mutant_one_hot = df[df['Mutant'] == mutant]['Mutant_OneHot'].values[0][interface]
                seq_one_hot = df[df['Sequence'] == seq]['Sequence_OneHot'].values[0][interface]
                if mutant_one_hot != seq_one_hot:
                    # append the data to the dataframe using concat
                    keep_mutant = False
            if keep_mutant == True:
                mutant_df = pd.concat([mutant_df, seq_df[seq_df['Mutant'] == mutant]])
        # concat the mutant_df with the output_df
        output_df = pd.concat([output_df, mutant_df])
    
    # remove the one-hot encoding columns
    output_df = output_df.drop(columns=['Sequence_OneHot', 'Mutant_OneHot'])
    # save the output dataframe to a csv file
    output_df.to_csv(f'{output_dir}/{output_file}', index=False)