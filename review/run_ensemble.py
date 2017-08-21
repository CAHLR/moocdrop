import pandas as pd
import numpy as np
from sklearn.ensemble import *
from sklearn.svm import SVC
from sklearn.neighbors import NearestNeighbors
from sklearn.linear_model import LogisticRegression
from sklearn.cross_validation import train_test_split
from sklearn import metrics
from sklearn.cross_validation import cross_val_score
# Initializing lists to hold the AUC scores after cross-validation

aucensemble=[]
auclogistic=[]
aucsvm=[]
aucrandomforests=[]
aucnearestneighbors=[]

# 3 training-test sets for the cross-validation

'''testdata = pd.read_csv('/deepedu/research/moocdrop/code/harman/FEATURES_BerkeleyX-Stat_2.1x-1T2014.csv')
traindata = pd.read_csv('/deepedu/research/moocdrop/code/harman/FEATURES_DelftX-EX101x-1T2015.csv')
df = pd.read_csv('/deepedu/research/moocdrop/code/harman/FEATURES_DelftX-AE1110x-1T2014.csv')

testdata = pd.read_csv('/deepedu/research/moocdrop/code/harman/FEATURES_DelftX-AE1110x-1T2014.csv')
traindata = pd.read_csv('/deepedu/research/moocdrop/code/harman/FEATURES_BerkeleyX-Stat_2.1x-1T2014.csv')
df = pd.read_csv('/deepedu/research/moocdrop/code/harman/FEATURES_DelftX-EX101x-1T2015.csv')'''

testdata = pd.read_csv('/deepedu/research/moocdrop/code/harman/FEATURES_DelftX-EX101x-1T2015.csv')
traindata = pd.read_csv('/deepedu/research/moocdrop/code/harman/FEATURES_DelftX-AE1110x-1T2014.csv')
df = pd.read_csv('/deepedu/research/moocdrop/code/harman/FEATURES_BerkeleyX-Stat_2.1x-1T2014.csv')

traindata.append(df)

ypredictweek=[]
ytestweek=[]
errorweek=[]
for i in range(1,6):
    test=testdata[testdata.week == i]       #Dividing data into test and training set.
    train=traindata[traindata.week == i]

    X=train.iloc[:,3:-1]            #Dividing data into input and output for models
    Xtest=test.iloc[:,3:-1]

    y=train['Stopped']
    ytest=test['Stopped']
    y = np.ravel(y)
    ytest=np.ravel(ytest)

    lr = LogisticRegression()     #Logistic Regression
    lr = lr.fit(X, y)
    model1y=lr.predict(Xtest)

    rfc=RandomForestClassifier()  #RandomForests
    rfc = rfc.fit(X,y)
    model2y=rfc.predict(Xtest)

    svm=SVC()                     #Support Vector Machine
    svm = svm.fit(X,y)
    model3y=svm.predict(Xtest)

    from sklearn.neighbors import KNeighborsClassifier
    knn = KNeighborsClassifier()
    knn = knn.fit(X,y)
    model4y=knn.predict(Xtest)    #Nearest Neighbors

    model1y=model1y.tolist()
    model2y=model2y.tolist()
    model3y=model3y.tolist()
    model4y=model4y.tolist()
    ytest=ytest.tolist()

    # Error calculation for ensemble and all the individual 4 models

    ypredict=[float(model1y[n]+model2y[n]+model3y[n]++model4y[n])/4 for n in range(len(model1y))] #Ensemble
    # ypredict=model1y
    # ypredict=model2y
    # ypredict=model3y
    # ypredict=model4y
    error=[abs(ytest[n]-ypredict[n]) for n in range(len(model1y))]                    #Error for each element
    error=sum(error)/len(error)                                                       #Average Error Per Student

    ypredictweek.append(ypredict)
    ytestweek.append(ytest)
    errorweek.append(error)


for i in range(6):
    print('Week'+str(i+1))
#    print('Prediction: '+ str(ypredictweek[i]))
#    print('Actual Values:'+ str(ytestweek[i]))
    print('Errors:'+ str(errorweek[i]))
    print('\n\n')

#AUC metrics calulation for the 5 (ensemble and 4 individual) models


aucweek=[]
for i in range(1,6):
    auc=metrics.roc_auc_score(ytestweek[i-1],ypredictweek[i-1])
    print(i, auc)
    aucweek.append(auc)

aucensemble.append(aucweek)
# auclogistic.append(aucweek)
# aucrandomforests.append(aucweek)
# aucsvm.append(aucweek)
# aucnearestneighbors.append(aucweek)



