import collect_data_lstm_live_data
import run_lstm_util_live_data
from collections import defaultdict
import numpy as np
from keras.utils import np_utils
from keras.preprocessing import sequence
import pandas as pd
import os
import sys

#files uses to pull course information and course users
log_file = "berkeleyx-edx-cs169-2x-events.log"
course = "BerkeleyX-CS169.2x-1T2017"

#input = event_log_file_name as address to the log file
#output = stores log in ordered format at ORDERED_event_log_file_name
collect_data_lstm_live_data.generate_ordered_event_copy(log_file)

ordered_course_file_log = 'ORDERED_'+log_file
with open(ordered_course_file_log) as f:
	ordered_event_list = f.readlines()

#outputs actions chronologically sorted by each student
student_sorted = collect_data_lstm_live_data.stusort(ordered_event_list)

#convert student sorted actions into sequence of integers
if not os.path.exists("RNN_event_list.csv"):
    raise IOError("No list of RNN Events")

event_stream_per_student = defaultdict(list)
ce_types = collect_data_lstm_live_data.get_ce_types()
# Get events from log_file
for u_name, actions in student_sorted.items():
    for line in actions:
        try:
            parsed_event = collect_data_lstm_live_data.parse_event(line)
        except ValueError:
        	#unable to parse action
            print(line)
            continue
        time_element = line['time']
        username = line['username']
        if parsed_event in ce_types:
	        event_stream_per_student[u_name].append(ce_types[parsed_event])
events_df = pd.DataFrame({'username': list(event_stream_per_student.keys()), 'seq': list(event_stream_per_student.values())})

# For CS169, user action ceiling chosen as 7000 and |types of actions| == 88
max_seq_len = 7000
max_input_dim = 88
events_df.reset_index(drop=True, inplace=True)
events_df.reindex(np.random.permutation(events_df.index))
event_list = events_df['seq'].values

event_list_binary = [np_utils.to_categorical(x, max_input_dim) for x in event_list]
x_train = sequence.pad_sequences(event_list_binary, maxlen=max_seq_len, dtype='int32',
                                     padding='post', truncating='post')

#load model weights
#returns the probability the student will attrit after 2 days of his last action
attr_model = run_lstm_util_live_data.load_keras_weights_from_disk('models', 'attr')
out = attr_model.predict(x_train)
prediction = out[:, -1, 0]
prediction = np.round(100 * prediction)
events_df['attrition_prediction'] = prediction

comp_model = run_lstm_util_live_data.load_keras_weights_from_disk('models', 'comp')
out2 = comp_model.predict(x_train)
prediction2 = out2[:, -1, 0]
prediction2 = np.round(100 * prediction2)
events_df['completion_prediction'] = prediction2

cert_model = run_lstm_util_live_data.load_keras_weights_from_disk('models', 'cert')
out3 = cert_model.predict(x_train)
prediction3 = out3[:, -1, 0]
prediction3 = np.round(100 * prediction3)
events_df['certification_prediction'] = prediction3

#enriches data with user information
user_info = pd.read_csv('MASTER_user_info.csv')
new_master_df = pd.merge(events_df, user_info, how='left', on='username')
new_master_df = new_master_df.dropna(axis=0, subset=['anon_user_id'])


header = ["anon_user_id", "attrition_prediction", "completion_prediction", "certification_prediction"]
new_master_df.to_csv('prediction.csv', index=False, columns = header)
print ("Updated predictions at prediction.csv")
sys.exit()
