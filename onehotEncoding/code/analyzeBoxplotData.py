import os, sys, pandas as pd
import matplotlib.pyplot as plt


if __name__ == '__main__':
    # get the command line arguments
    input_dir = sys.argv[1]
    output_dir= sys.argv[2]

    # make the output directory if it doesn't exist
    os.makedirs(name=output_dir, exist_ok=True)
    count = 100

    # read through files in the input directory
    for file in os.listdir(input_dir):
        # get the input file
        input_file = os.path.join(input_dir, file)
        # get the file name
        file_name = os.path.splitext(file)[0]
        # read the input file as a dataframe
        df = pd.read_csv(input_file)

        # only keep the data where the count is greater than the desired count of AA combinations
        df = df[df['count'] > count]

        df = df[df['mean'] > 70]
        # make a scatter plot of the data mean and standard deviation
        plt.scatter(df['count'], df['mean'])
        # add in the standard deviation
        #plt.errorbar(df['count'], df['mean'], yerr=df['std'], fmt='o', color='blue', ecolor='black', elinewidth=1, capsize=2)
        # save the plot
        plt.savefig(f'{output_dir}/{file_name}.png')
        # reset the plot
        plt.clf()
        # print the max mean row
        #print(df[df['mean'] == df['mean'].max()])
        print(df)
        #exit(0)



            # if I have to, I can also go back to my plot code and just change it so that it only plots the good ones/ ones with more than this count
            





        # write the dataframe to a csv file
        #output_file = f'{output_dir}/{file}'
        #df.to_csv(output_file, index=False)

