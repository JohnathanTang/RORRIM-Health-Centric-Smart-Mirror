import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
import joblib

from sklearn.model_selection import train_test_split, GridSearchCV, KFold
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.metrics import confusion_matrix
from sklearn.metrics import f1_score
from sklearn.metrics import accuracy_score, mean_squared_error

KNN_CURR_DIR="user_data/"

class KNN():
    def __init__(self):
        self.model = joblib.load(KNN_CURR_DIR+'KNN_Model.joblib')
     
    @staticmethod  
    def make_model():
        dataset = pd.read_csv("PhysioNet/NonEEG_CSV/subject_stages.csv")

        x = dataset.drop(columns=['Subject #', 'Age', 'Gender', 'Height (cm)', 'Weight (kg)', 'AccelX', 'AccelY', 'AccelZ', 'EDA', 'Stage'])

        y = dataset['Stage']
        X_train, x_valid, Y_train, y_valid = train_test_split(x.values, y.values, test_size=0.2)

        sc_x = StandardScaler()

        X_train = sc_x.fit_transform(X_train)
        x_valid = sc_x.transform(x_valid)

        kf = KFold(n_splits=5)
        max_score = 0
        best_classifier = None

        for train_index, test_index in kf.split(X_train):
            x_train, x_test = X_train[train_index], X_train[test_index]
            y_train, y_test = Y_train[train_index], Y_train[test_index]

            classifier = KNeighborsClassifier(n_neighbors=5, p=2, metric='euclidean')
            classifier.fit(x_train, y_train)

            y_pred = classifier.predict(x_test)
            testing_score = accuracy_score(y_test, y_pred)
            #print("Testing score = ", testing_score)

            y_pred_valid = classifier.predict(x_valid)
            valid_score = accuracy_score(y_valid, y_pred_valid)
            #print("Validation score = ", valid_score)

            #print("Mean squared = ", mean_squared_error(y_valid, y_pred_valid))

            if valid_score > max_score:
                max_score = valid_score
                best_classifier = classifier
        
        joblib.dump(classifier,'user_data/KNN_Model.joblib')
        joblib.dump(sc_x,'user_data/std_scaler.bin',compress=True)


    def predict(self,tempf,spo2,hr):
        
        sc=joblib.load(KNN_CURR_DIR+'std_scaler.bin')
        tempc = (tempf - 32) * 5/9
        x = sc.transform([[tempc,spo2,hr]])
        #print(tempc)
        prediction = self.model.predict(x)
        #print(prediction)
        return prediction[0]
    
if __name__=="__main__":
    
    KNN_CURR_DIR=""

