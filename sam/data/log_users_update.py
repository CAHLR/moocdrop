######### GOAL: #########
# update user info table at 'MATSER_user_info.csv'

import pandas as pd
import numpy as np

################## USER INFO UPDATE PART
######### parse new user information
# read in files
student_details = pd.DataFrame(pd.read_table('BerkeleyX-CS169.2x-1T2017SP-auth_user-prod-analytics.sql'))
student_anon = pd.DataFrame(pd.read_table('BerkeleyX-CS169.2x-1T2017SP-student_anonymoususerid-prod-analytics.sql'))
student_details = pd.concat([student_details,student_anon])
student_details = student_details.loc[:,['first_name','last_name', 'id','username','email']]
student_details = student_details.drop_duplicates().reset_index(drop=True)

# parse info and prepare dataframe
actual_user_id = student_anon.user_id.tolist()
assigned_user_id = student_anon.id.tolist()
master_df = pd.DataFrame({'actual_user_id':actual_user_id,"assigned_user_id":assigned_user_id})
email_df = pd.DataFrame({'first_name':student_details.first_name.tolist(),'last_name':student_details.last_name.tolist(),'actual_user_id':student_details.id.tolist(), 'username':student_details.username.tolist(),'email':student_details.email.tolist()})
master_df = pd.merge(master_df, email_df, how='outer', on='actual_user_id')
master_df["anon_user_id"] = np.nan

# add header
old_user_df = pd.read_csv('MASTER_user_info.csv')
previous_anon_value = int(len(old_user_df))
updated_df = pd.concat([old_user_df,master_df]).drop_duplicates('username').reset_index(drop=True)

#assign anonIds to rows without anonIds
for index, row in updated_df.loc[updated_df['anon_user_id'].isnull()].iterrows():
    updated_df.iloc[index,1] = previous_anon_value
    previous_anon_value +=1

updated_df.to_csv('MASTER_user_info.csv', index=False, header=['actual_user_id','anon_user_id','assigned_user_id','email','first_name','last_name','username'])
print ("Updated User Info")
