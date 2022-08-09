from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from matplotlib import pyplot as plt

"""
This script is used to test the Linear Regression algorithm on my dataset. It will be the basis
for any future linear regression analysis that I do (energy scores, )

Some of this code comes from: https://www.youtube.com/watch?v=b0L47BeklTE&ab_channel=RylanFowers 
"""
# get the datafile from command line argument
dataFile = sys.argv[1]

# read dataFile into a dataframe
data = pd.read_csv(dataFile)

# set the x values equal to energy scores (vdw, hbond, solvation)
#TODO: learn how to input more than one variable into the Linear Regression
x = data['Total Energy']
# set the y values equal to the fluorescence
y = data['Fluorescence']

# show plots for each energy score


# show the training vs testing data on a scatterplot
plt.scatter(x_train, y_train, label='Training Data', color='red')
plt.scatter(x_test, y_test, label='Testing Data', color='blue')
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=0)

LR = LinearRegression()
LR.fit(x_train.values.reshape(-1,1), y_train.values)
# Use model to predict on test data
predictions = LR.predict(x_test.values.reshape(-1,1))

# plot predictions vs actual values
plt.plot(x_test, predictions, label='Linear Regression', color='green', linewidth=3)



# added in by copilot; could be helpful
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import explained_variance_score


