# ensembleresults=[]
# logisticresults=[]
# randomforestsresults=[]
# svmresults=[]
# nearestneighborsresults=[]

# Averaging of the results for cross-validation for each of the 5 models

for i in range(5):
    ensembleresults.append((aucensemble[0][i]+aucensemble[1][i]+aucensemble[2][i])/3)
    logisticresults.append((auclogistic[0][i]+auclogistic[1][i]+auclogistic[2][i])/3)
    randomforestsresults.append((aucrandomforests[0][i]+aucrandomforests[1][i]+aucrandomforests[2][i])/3)
    svmresults.append((aucsvm[0][i]+aucsvm[1][i]+aucsvm[2][i])/3)
    nearestneighborsresults.append((aucnearestneighbors[0][i]+aucnearestneighbors[1][i]+aucnearestneighbors[2][i])/3)

ensembleres=['Ensemble']+ensembleresults
logisticres=['Logistic Regression']+logisticresults
randomforestsres=['Random Forests']+randomforestsresults
svmres=['SVM']+svmresults
nearestneighborsres=['Nearest Neighbors']+nearestneighborsresults

#Writing final results to a data frame

res=[ensembleres, logisticres, randomforestsres, svmres, nearestneighborsres]
header=['Model','Week 1','Week 2','Week 3','Week 4','Week 5']
results=pd.DataFrame(res, columns=header)
results

#Writing final results into a CSV file

results.to_csv('Results.csv')