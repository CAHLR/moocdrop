# Import statements

import numpy as np
import pandas as pd

# Commands to read the 3 course files into the code

# data = pd.read_csv('/deepedu/research/moocdrop/code/rachel/FEATURES_BerkeleyX-Stat_2.1x-1T2014.csv')
# data = pd.read_csv('/deepedu/research/moocdrop/code/rachel/FEATURES_DelftX-AE1110x-1T2014.csv')
data = pd.read_csv('/deepedu/research/moocdrop/code/rachel/FEATURES_DelftX-EX101x-1T2015.csv')

# Commands to read the 3 certificate files into the code

# certificate_file = "/deepedu/research/moocdrop/data/BerkeleyX-Stat_2.1x-1T2014-certificates_generatedcertificate-prod-analytics.sql"
# certificate_file = "/deepedu/research/moocdrop/data/DelftX-AE1110x-1T2014-certificates_generatedcertificate-prod-analytics.sql"
certificate_file = "/deepedu/research/moocdrop/data/DelftX-EX101x-1T2015-certificates_generatedcertificate-prod-analytics.sql"

# Commands to fetch user IDs of students with information about whether they got cerified

cert_df = pd.read_table(certificate_file)
students_passing = cert_df.user_id[cert_df['status'] == 'downloadable']
sp_list = ["username_" + str(index) for index in students_passing.tolist()]

# column named 'Stopped' for the course data frame. A value of 1 indicates that the student
# stopped/was not certified and a value of 0 indicates that the student was certified.

def f(row):
    if row['status'] == 'notpassing':
        val = 1
    else:
        val = 0
    return val

cert_df['Stopped'] = cert_df.apply(f, axis=1)
cert_df=cert_df[['user_id','Stopped']]

#Merging certification data with the original data frame

dta = pd.merge(data,cert_df,how='left',on='user_id')

#Setting default values for the features (in case of NaN values)

dta['feature1'].fillna(0, inplace=True)
dta['feature2'].fillna(0, inplace=True)
dta['feature3'].fillna(0, inplace=True)
dta['feature4'].fillna(0, inplace=True)
dta['feature5'].fillna(2000000000, inplace=True)
dta['feature6'].fillna(2000000000, inplace=True)
dta['feature7'].fillna(0, inplace=True)
dta['feature8'].fillna(0, inplace=True)
dta['feature9'].fillna(0, inplace=True)
dta['feature10'].fillna(0, inplace=True)
dta['Stopped'].fillna(1, inplace=True)

# Commands to write the resulting 3 dataframes for the 3 course files to CSVs.

# dta.to_csv('/deepedu/research/moocdrop/code/harman/FEATURES_BerkeleyX-Stat_2.1x-1T2014.csv')
# dta.to_csv('/deepedu/research/moocdrop/code/harman/FEATURES_DelftX-AE1110x-1T2014.csv')
dta.to_csv('/deepedu/research/moocdrop/code/harman/FEATURES_DelftX-EX101x-1T2015.csv')
