import os, sys, numpy as np, pandas as pd, matplotlib.pyplot as plt
from sklearn import preprocessing, svm
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error,mean_squared_error
import statsmodels.api as sm
 
def singleRegressionTraining(df, design, xAxis, yAxis):
    input_df = df[df['Sample'] == design]
    # get the x and y values
    x = input_df[xAxis].values.reshape(-1,1)
    y = input_df[yAxis].values.reshape(-1,1)

    # train the model
    model = LinearRegression().fit(x, y)

    # the below I got from: https://www.geeksforgeeks.org/python-linear-regression-using-sklearn/#
    X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.30, random_state=0)
    regr = LinearRegression()
    regr.fit(X_train, y_train)
    print("Regression Score:", regr.score(X_test, y_test))

    # plot the data
    y_pred = regr.predict(X_test)
    plt.scatter(X_test, y_test, color='black')
    plt.plot(X_test, y_pred, color='blue', linewidth=3)
    plt.xlabel(xAxis)
    plt.ylabel(yAxis)
    plt.title(label=f'{design} {xAxis} vs {yAxis}')

    # save the plot and close
    plt.savefig(f'{outputDir}/{design}_{xAxis}.png')
    plt.clf()

    #squared True returns MSE value, False returns RMSE value.
    mae = mean_absolute_error(y_true=y_test,y_pred=y_pred)
    mse = mean_squared_error(y_true=y_test,y_pred=y_pred) #default=True
    rmse = mean_squared_error(y_true=y_test,y_pred=y_pred,squared=False)
    print("MAE:",mae)
    print("MSE:",mse)
    print("RMSE:",rmse)

# from https://datatofish.com/multiple-linear-regression-python/ as a way to get weights for the regression on multiple variables
def weightedRegressionTraining(df, design, xAxes, yAxis):
    x = input_df[xAxes]
    y = input_df[yAxis]

    # with sklearn
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
# read in command line arguments
dataFile = sys.argv[1]
outputDir = sys.argv[2]

os.makedirs(name=outputDir, exist_ok=True)

# read in the data file
df = pd.read_csv(dataFile)



# hardcoded: choose which columns to use for the regression
xAxes = ['HBONDDiff', 'VDWDiff', 'IMM1Diff']
yAxis = 'PercentGpA'

# remove any rows where sample is NA
df = df[df['Sample'].notna()]
# hardcoded: getting rid of possible outliers
df = df[df[yAxis] < 1.4]
df.to_csv(f'{outputDir}/data.csv', index=False)
df = df[df['VDWDiff'] < 0]
df = df[df['VDWDiff'] > -60]

# loop through the design types
for design in df['Sample'].unique():
    for xAxis in xAxes:
        singleRegressionTraining(df, design, xAxis, yAxis)
    weightedRegressionTraining(df, design, xAxes, yAxis)

    # TODO: the above works for a single model, but I think I would want to train multiple models and then compare them?
    # This might allow me to start to do that: https://www.techwithtim.net/tutorials/machine-learning-python/saving-models
    # And this has some code to visualize predicted vs actual: https://www.kdnuggets.com/2019/03/beginners-guide-linear-regression-python-scikit-learn.html
    # also if wanting to test multiple regressions, the lower root mean squared error is better so could use that to evaluate
    # TODO: it seems that people return models; possibly to do something with them after? or to call their scores?:
    # https://saturncloud.io/blog/how-to-train-a-model-twice-multiple-times-in-scikitlearn-using-fit/
    # TODO: these graphs look helpful: https://www.scribbr.com/statistics/simple-linear-regression/