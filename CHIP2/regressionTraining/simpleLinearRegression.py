import os, sys, numpy as np, pandas as pd, matplotlib.pyplot as plt
from sklearn import preprocessing, svm
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error,mean_squared_error
import statsmodels.api as sm
 

# read in command line arguments
dataFile = sys.argv[1]
outputDir = sys.argv[2]

os.makedirs(name=outputDir, exist_ok=True)
# read in the data file
df = pd.read_csv(dataFile)

# get the differences in energy
cols = ['HBOND', 'VDW', 'IMM1']
for col in cols:
    df[f'{col}Diff'] = df[f'{col}DimerOptimize'] - df[f'{col}Monomer']

#TODO: I think that this script is getting complex; simplify it
# hardcoded: getting rid of outliers in vdw
df = df[df['VDWDiff'] < 0]
df = df[df['VDWDiff'] > -60]

# hardcoded: choose which columns to use for the regression
xAxis = ['HBONDDiff', 'VDWDiff', 'IMM1Diff']
yAxis = 'PercentGpA'

# remove any rows where sample is NA
df = df[df['Sample'].notna()]
df = df[df[yAxis] < 1.4]
#df = df[df[xAxis] < 2]
#df = df[df[yAxis] > 0.35]
df.to_csv(f'{outputDir}/data.csv', index=False)

# loop through the design types
for design in df['Sample'].unique():
    for xAx in xAxis:
        input_df = df[df['Sample'] == design]
        # get the x and y values
        #x = input_df[xAxis].values.reshape(-1,1)
        #y = input_df[yAxis].values.reshape(-1,1)
        x = input_df[xAx].values.reshape(-1,1)
        y = input_df[yAxis].values.reshape(-1,1)
        # TODO: below train the model on the x and y axis
        model = LinearRegression().fit(x, y)

        # the below I got from: https://www.geeksforgeeks.org/python-linear-regression-using-sklearn/#
        X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.75, random_state=0)

        regr = LinearRegression()

        regr.fit(X_train, y_train)
        print(regr.score(X_test, y_test))

        y_pred = regr.predict(X_test)
        plt.scatter(X_test, y_test, color='black')
        plt.plot(X_test, y_pred, color='blue', linewidth=3)

        # save the plot
        plt.savefig(f'{outputDir}/{design}_{xAx}.png')
        plt.clf()
        # TODO: I also have a script from a year ago in clusterAnalysis/code/linearRegression.py; could look at that for more detail and can't remember if it worked?
        # that same directory also has some clustering code, and now with actual experimental data, could be used to cluster for meaningful data?

        #squared True returns MSE value, False returns RMSE value.
        mae = mean_absolute_error(y_true=y_test,y_pred=y_pred)
        mse = mean_squared_error(y_true=y_test,y_pred=y_pred) #default=True
        rmse = mean_squared_error(y_true=y_test,y_pred=y_pred,squared=False)
        print("MAE:",mae)
        print("MSE:",mse)
        print("RMSE:",rmse)
    # TODO: use this to get weights: https://datatofish.com/multiple-linear-regression-python/
    x = input_df[xAxis]
    y = input_df[yAxis]

    regr = LinearRegression()
    regr.fit(x, y)

    print('Intercept: \n', regr.intercept_)
    print('Coefficients: \n', regr.coef_)

    # with statsmodels
    x = sm.add_constant(x) # adding a constant
    
    model = sm.OLS(y, x).fit()
    predictions = model.predict(x) 
    
    print_model = model.summary()
    print(print_model)