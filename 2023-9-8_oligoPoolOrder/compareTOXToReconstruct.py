import os, sys, pandas as pd, numpy as np, matplotlib.pyplot as plt

def plot_and_get_regression(df_control_plot, xaxis_col, yaxis_col, sample):
    xaxis = df_control_plot[xaxis_col]
    yaxis = df_control_plot[yaxis_col]
    plt.scatter(xaxis, yaxis)
    # plot the line of best fit
    m, b = np.polyfit(xaxis, yaxis, 1)
    plt.plot(xaxis, m*xaxis + b)
    
    # plot the standard deviation for each point
    std_x = df_control_plot['PercentStandardDev']
    #std_y = df_control_plot['std_adjusted']
    std_y = df_control_plot['FluorStdDev']
    #std_x = df_control_plot['Percent GpA stdev']
    #std_y = df_control_plot['std']
    plt.errorbar(xaxis, yaxis, yerr=std_y, xerr=std_x, fmt='none', ecolor='black')
    #plt.xlabel(xaxis_col)
    #plt.ylabel(yaxis_col)
    plt.xlabel('TOXGREEN Percent GpA')
    plt.ylabel('Reconstructed Fluorescence')
    plt.title(sample)
    # add the equation to the plot
    plt.text(0.05, 0.95, f'y = {m:.2f}x + {b:.2f}', transform=plt.gca().transAxes)
    # add the r^2 value to the plot
    plt.text(0.05, 0.90, f'r^2 = {np.corrcoef(xaxis, yaxis)[0,1]**2:.2f}', transform=plt.gca().transAxes)
    plt.savefig(f'{outputDir}/{sample}_fit.png')
    plt.clf()
    return m, b

# read in the command line arguments
toxgreenFile = sys.argv[1]
reconstructionFile = sys.argv[2]
outputDir = sys.argv[3]

# make the output directory
os.makedirs(outputDir, exist_ok=True)

reconstructionCols = ['Sequence', 'PercentGpA_transformed', 'std_adjusted', 'Sample', 'Fluorescence', 'FluorStdDev']
toxgreenCols = ['Sequence', 'PercentGpA', 'PercentStandardDev']

# read in the input files
df_toxgreen = pd.read_csv(toxgreenFile)
df_reconstruction = pd.read_csv(reconstructionFile)


# if toxgreen sequences end with ili, remove the ili
df_toxgreen['Sequence'] = df_toxgreen['Sequence'].str.replace('ILI$', '')

# keep the sequences that are in the toxgreen dataframes
df_reconstruction = df_reconstruction[df_reconstruction['Sequence'].isin(df_toxgreen['Sequence'])]
print(df_reconstruction)
print(df_toxgreen)

# make a new dataframe with the percent GpA and std for each sequence
df_both = pd.DataFrame()

# concatenate the dataframes on the sequence column
df_both = pd.merge(df_toxgreen[toxgreenCols], df_reconstruction[reconstructionCols], on='Sequence', how='inner')

# plot the data
xaxis = 'PercentGpA'
#yaxis = 'PercentGpA_transformed'
yaxis = 'Fluorescence'
for sample in df_both['Sample'].unique():
    df_sample = df_both[df_both['Sample'] == sample]
    plot_and_get_regression(df_sample, 'PercentGpA', yaxis, sample)

