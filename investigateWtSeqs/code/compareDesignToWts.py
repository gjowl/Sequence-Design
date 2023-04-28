import os, sys, pandas as pd

# read the command line arguments
design_file = sys.argv[1]
wt_file = sys.argv[2]

# read the input file as a dataframe
df = pd.read_csv(design_file, sep=',', dtype={'Interface': str})
wt_df = pd.read_csv(wt_file, sep=',')

# loop through the sequences
output_df = pd.DataFrame()
for interface in df['Interface'].unique():
    wt_interface_df = wt_df.copy()
    # make a new column with the interface string of the wt, skip any Xs
    wt_interface_df['Interface1'] = wt_interface_df['Aligned Seq 1'].apply(lambda x: ''.join([aa if interface[i] == '1' and aa != 'X' else '' for i, aa in enumerate(x)]))
    wt_interface_df['Interface2'] = wt_interface_df['Aligned Seq 2'].apply(lambda x: ''.join([aa if interface[i] == '1' and aa != 'X' else '' for i, aa in enumerate(x)]))
    # keep only the rows with matching interface
    df_interface = df[df['Interface'] == interface]
    for sequence in df_interface['Sequence'].unique():
        # keep the string for positions where interface is 1
        interface_str = ''.join([aa if interface[i] == '1' else '' for i, aa in enumerate(sequence)])
        print(f'{sequence}\n{interface_str}\n')
        # keep the rows where the interface string matches 4 or more positions
        test_list = ['AFGGGGGG', 'GFGGGGGG']
        count_list = []
        for wt_interface in wt_interface_df['Interface1']:
            count = sum([l1 == l2 for l1, l2 in zip(wt_interface, interface_str)])
            count_list.append(count)
        wt_interface_df['InterfaceCount'] = count_list
        # check how many positions within a string match
        matching_df = wt_interface_df[wt_interface_df['InterfaceCount'] >= 5].copy()
        # add the sequence to the dataframe
        matching_df['Sequence_Match'] = sequence
        matching_df['Interface_Match'] = interface_str
        # check if dataframe is empty
        if matching_df.empty:
            continue
        else:
            output_df = pd.concat([output_df, matching_df])

# save the output dataframe
output_df.to_csv('test_wt.csv', index=False)