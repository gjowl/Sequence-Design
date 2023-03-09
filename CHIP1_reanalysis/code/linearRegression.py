import os, sys, pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn import preprocessing, svm
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression as lr

# read in the data from command line
data = sys.argv[1]
outputDir = sys.argv[2]

# make the output directory if it doesn't exist
os.makedirs(name=outputDir, exist_ok=True)

# read in the data to a dataframe
df = pd.read_csv(data)

x = np.array(df['Total'].values.reshape(-1,1))
y = np.array(df['Fluorescence'].values.reshape(-1,1))

X_train, X_test, y_train, y_test = train_test_split(x, y, test_size = 0.25)

regr = lr()
regr.fit(X_train, y_train)
print(regr.score(X_test, y_test))

# plot the data
y_pred = regr.predict(X_test)
plt.scatter(X_test, y_test, color ='b')
plt.plot(X_test, y_pred, color ='k')

# save the plot
plt.savefig(f'{outputDir}/linearRegression.png')