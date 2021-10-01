import pandas as pd
import numpy as np
import sklearn as sk
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

#print("Reading file")
data = pd.read_csv("PhysioNet/NonEEG_CSV/SPO2HR/clean_pppoopoo.csv")
#print("File Read")

X = data.drop(['SPO2'], axis=1)

Y = data['SPO2']
Y = Y.values.reshape(-1,1)

random=700

days=[i for i in range(Y.size)]

clf = LinearRegression()
clf.fit(X,Y)


input = np.array([[1]])

input = input.reshape(1, -1)

print("SPO2 Prediction: ",clf.predict(input))

